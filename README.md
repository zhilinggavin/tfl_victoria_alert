# 🚇 TfL Victoria Line Email Alert Bot

## Automated line-status monitoring with uv + GitHub Actions

This project automatically checks the live status of selected London Underground lines (e.g., Victoria and Circle lines) using the public **TfL Unified API**, and sends an **email alert** when disruptions occur.
It runs completely in the cloud via **GitHub Actions**, so it works 24/7 even when your computer is off.

A complete system like this:

```TfL API → Cloud Function → Scheduled Trigger → Email → Your Gmail Inbox```

---

## 🌟 Features

* Monitors one or more Tube lines (Victoria Line by default)
* Uses the free TfL **Line Status API** (no API key required)
* Sends an email alert when:

  * Severe Delays
  * Part Suspended
  * Suspended
  * Service Closed
* Runs automatically on a schedule (default: every 5 minutes)
* Fully cloud-hosted using **GitHub Actions**
* Uses **uv** for fast, modern Python dependency management

---

## 🗂 Project Structure

```
tfl_victoria_alert/
│── .github/
│    └── workflows/
│         └── tfl-alert.yml      # GitHub Actions scheduled workflow
│── src/
│    └── tfl_victoria_alert/
│         └── main.py            # Main alert script
│── .env                         # Local email credentials (NOT in repo)
│── pyproject.toml               # uv project config
│── uv.lock                      # uv lockfile
│── README.md
```

---

## 🛠 Local Development (with uv)

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync the environment

```bash
uv sync
```

### 3. Run the alert script

```bash
uv run tfl-alert
```

---

## 🔑 Environment Variables (local `.env` file)

Create a `.env` file in the project root:

```python
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=your_gmail+alerts@gmail.com
```

### Gmail App Password

Gmail requires a **16-digit App Password**.
Create one at:

[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

(Regular passwords will not work.)

---

## 📡 How It Works

The script calls:

```
https://api.tfl.gov.uk/Line/victoria,circle/Status?detail=true
```

Then evaluates the status:

* If the line is **Good Service** → do nothing
* If the line is **Severe Delays / Suspended / Part Suspended / Service Closed** → send email

GitHub Actions runs this check automatically every 5 minutes.

---

## ☁️ Cloud Deployment (GitHub Actions)

### 1. Add repository secrets

Go to:

**GitHub → Repo → Settings → Secrets → Actions**

Add:

* `EMAIL_ADDRESS`
* `EMAIL_PASSWORD`
* `EMAIL_TO`

### 2. Add workflow file

`.github/workflows/tfl-alert.yml`

This workflow:

* Installs uv
* Syncs dependencies
* Runs the script on a schedule
* Works even when your PC is off

---

## 🕒 Default Schedule

```yaml
schedule:
  - cron: "*/5 * * * *"   # Every 5 minutes
```

You can change it to:

* Every 10 minutes: `*/10 * * * *`
* Once every morning at 7:00: `0 7 * * *`

---

## 🧪 Manual Trigger

You can run the bot manually from:
**GitHub → Actions → TfL Victoria Alert Bot → Run workflow**

---

## 📦 Dependencies

Installed via uv:

* `requests`
* `python-dotenv`
* your project package (`tfl-victoria-alert`)

---

## 🧩 Extending the Project

You can easily add:

* Monitoring more Tube lines
* Bus arrival alerts
* Slack/Telegram notifications
* Daily morning status summaries
* Logging to Google Sheets
* Streamlit dashboard visualisation

---

## 📄 Licence

This project is released under the MIT licence.
TfL API usage is subject to TfL’s API Terms of Use.

---

## 🙌 Acknowledgements

* Transport for London (TfL) Unified API
* uv Python package manager
* GitHub Actions CI/CD platform

Happy commuting!
