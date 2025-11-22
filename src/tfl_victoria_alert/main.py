import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from dotenv import load_dotenv

load_dotenv()

TFL_APP_KEY = os.getenv("TFL_APP_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

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
        "Service Closed",
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
    statuses = get_line_status()
    
    for line_name, status in statuses.items():
        if should_alert(status):
            send_email(
                f"{line_name} Line Alert",
                build_body(line_name, status)
            )
            print(f"Email alert of {line_name} line sent.")
        else:
            print(f"{line_name} line OK")

if __name__ == "__main__":
    main()
