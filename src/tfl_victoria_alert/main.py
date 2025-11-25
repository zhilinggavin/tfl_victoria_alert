import json
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate

import requests
from dotenv import load_dotenv

load_dotenv()

TFL_APP_KEY = os.getenv("TFL_APP_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
ALERT_COOLDOWN_MINUTES = int(os.getenv("ALERT_COOLDOWN_MINUTES", "60"))
STATE_FILE = os.path.join(os.path.dirname(__file__), ".alert_state.json")

def get_line_status():
    """
    Fetch the status of the Victoria and Circle lines from TfL.
    No API key is required.
    """
    url = "https://api.tfl.gov.uk/Line/victoria,circle/Status?detail=true"

    headers = {
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    result = {}
    for line in data:
        name = line["name"]
        statuses = line["lineStatuses"]
        parsed = [
            (
                s.get("statusSeverityDescription", "Unknown"),
                s.get("reason", "")
            )
            for s in statuses
        ]
        result[name] = parsed

    return result


def should_alert(status_list):
    """
    status_list = list of (severity, reason).
    e.g. [('Service Closed', 'due to...')]
    """
    alert_levels = {
        "Severe Delays",
        "Part Suspended",
        "Suspended",
        # "Service Closed",
    }

    for severity, _ in status_list:
        if severity in alert_levels:
            return True
    return False


def build_body(line_name, status_list):
    text = []
    timestamp = formatdate(localtime=True)
    for severity, reason in status_list:
        text.append(f"Time: {timestamp}\n")
        text.append(f"Line: {line_name}\n")
        text.append(f"Status: {severity}\n")
        if reason:
            text.append(f"Reason: {reason}")
        text.append("")
    return "\n".join(text)


def load_alert_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_alert_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def normalize_status_list(status_list):
    return [[severity, reason] for severity, reason in status_list]


def should_skip_alert(line_name, status_list, state):
    entry = state.get(line_name)
    if not entry:
        return False

    last_status = entry.get("status")
    last_ts_str = entry.get("timestamp")

    if last_status != normalize_status_list(status_list):
        return False

    try:
        last_ts = datetime.fromisoformat(last_ts_str)
    except (TypeError, ValueError):
        return False

    cooldown = timedelta(minutes=ALERT_COOLDOWN_MINUTES)
    return datetime.now(timezone.utc) - last_ts < cooldown


def record_alert(line_name, status_list, state):
    state[line_name] = {
        "status": normalize_status_list(status_list),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("TfL Victoria Alert Bot", EMAIL_ADDRESS))
    msg["To"] = EMAIL_TO
    msg["X-Priority"] = "1"
    msg["X-MSMail-Priority"] = "High"
    msg["Importance"] = "High"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def main():
    state = load_alert_state()
    statuses = get_line_status()
    
    for line_name, status in statuses.items():
        if should_alert(status):
            if should_skip_alert(line_name, status, state):
                print(f"{line_name} alert suppressed (recently sent).")
                continue

            send_email(f"{line_name} Line Alert", build_body(line_name, status))
            record_alert(line_name, status, state)
            print(f"Email alert of {line_name} line sent.")
        else:
            state.pop(line_name, None)
            print(f"{line_name} line OK")

    save_alert_state(state)

if __name__ == "__main__":
    main()
