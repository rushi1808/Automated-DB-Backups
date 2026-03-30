# 🛡️ Intelligent Secure Automated Database Backup & Anomaly Detection System

> A production-level Python project automating MySQL database backups with **AES-256 encryption**, **Google Cloud Storage** integration, and **AI-powered Anomaly Detection** using Isolation Forest.

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Module Breakdown](#-module-breakdown)
- [Data Flow Diagram](#-data-flow-diagram)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Running the System](#-running-the-system)
- [Anomaly Detection – How It Works](#-anomaly-detection--how-it-works)
- [Security Model](#-security-model)
- [Troubleshooting](#-troubleshooting)

---

## ❗ Problem Statement

### The Real-World Challenge

In modern software systems, databases are the **most critical and vulnerable asset**. Organizations — from startups to enterprises — face the following persistent threats:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PROBLEMS IN THE REAL WORLD                          │
├──────────────────────────┬──────────────────────────────────────────────┤
│  ❌ Problem               │  💥 Impact                                  │
├──────────────────────────┼──────────────────────────────────────────────┤
│  Manual backups           │  Human error, missed schedules, no          │
│                          │  consistency — data loss is inevitable       │
├──────────────────────────┼──────────────────────────────────────────────┤
│  Unencrypted backups      │  A stolen .sql file = full data breach.     │
│                          │  Violates GDPR, IT Act 2000 compliance       │
├──────────────────────────┼──────────────────────────────────────────────┤
│  No off-site copy        │  Server crash or ransomware = permanent      │
│                          │  data loss with no recovery path             │
├──────────────────────────┼──────────────────────────────────────────────┤
│  Silent data attacks      │  Mass deletions or injections go unnoticed  │
│                          │  for hours/days — too late to recover        │
├──────────────────────────┼──────────────────────────────────────────────┤
│  No real-time alerting   │  Admins discover failures only after damage  │
│                          │  is done, with no audit trail                │
└──────────────────────────┴──────────────────────────────────────────────┘
```

### Attack Scenarios This System Defends Against

```
Scenario 1: Ransomware Attack
──────────────────────────────
  Attacker encrypts local server
        │
        ▼
  All local data inaccessible
        │
        ▼
  ✅ System Response: Encrypted backup already
     uploaded to Google Cloud Storage → restore
     from off-site copy, zero data loss


Scenario 2: Insider Threat / Mass Deletion
────────────────────────────────────────────
  Malicious employee runs DELETE FROM users
        │
        ▼
  row_count drops drastically in seconds
        │
        ▼
  ✅ System Response: Isolation Forest detects
     statistical anomaly → SMTP alert fires to
     admin within minutes → backup used to restore


Scenario 3: Backup File Theft
───────────────────────────────
  Attacker copies backup files from server
        │
        ▼
  Opens .enc file — sees only ciphertext
        │
        ▼
  ✅ System Response: AES-256 encryption makes
     backup files useless without the secret key
     stored separately in .env


Scenario 4: Admin Goes on Leave / Forgets Backup
──────────────────────────────────────────────────
  No human action taken for weeks
        │
        ▼
  ✅ System Response: scheduler.py runs backup
     pipeline daily — fully autonomous, zero
     human intervention needed
```

### Gap Analysis — Existing Solutions vs This System

```
┌─────────────────────┬───────────┬───────────┬──────────────────────┐
│  Feature            │  Manual   │  Basic    │  This System         │
│                     │  Backup   │  Script   │                      │
├─────────────────────┼───────────┼───────────┼──────────────────────┤
│  Automated schedule │     ❌    │     ✅    │         ✅           │
│  AES-256 encryption │     ❌    │     ❌    │         ✅           │
│  Cloud off-site DR  │     ❌    │     ❌    │         ✅           │
│  AI anomaly detect  │     ❌    │     ❌    │         ✅           │
│  Real-time alerts   │     ❌    │     ❌    │         ✅           │
│  Admin dashboard    │     ❌    │     ❌    │         ✅           │
│  Auto retention mgmt│     ❌    │     ❌    │         ✅           │
└─────────────────────┴───────────┴───────────┴──────────────────────┘
```

### Proposed Solution

This project proposes an **end-to-end intelligent backup system** that:

1. **Automates** the entire backup lifecycle (dump → compress → encrypt → upload → purge)
2. **Secures** backups with AES-256 encryption so stolen files are worthless
3. **Monitors** database health using an unsupervised ML model (Isolation Forest) to catch attacks in real-time
4. **Alerts** administrators instantly via email when anything goes wrong
5. **Provides** a web dashboard for manual control and visibility

> **Domain:** Database Security · Cloud Computing · Machine Learning  
> **Type:** Full-stack Python automation system with AI component  
> **Audience:** System administrators, DevOps engineers, small-to-mid scale organizations

---

## 🔍 Overview

This system solves the critical real-world problem of **unattended, secure, and intelligent database protection**. It combines:

| Capability | Technology |
|---|---|
| Automated Backup | `mysqldump` + `schedule` |
| Compression | ZIP archive |
| Encryption | AES-256 via `cryptography` (Fernet) |
| Cloud Storage | Google Cloud Storage API |
| Anomaly Detection | Scikit-Learn Isolation Forest |
| Alerting | SMTP Email |
| Dashboard | Flask Web UI |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SYSTEM ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌──────────────┐     triggers      ┌──────────────────────────┐   │
│   │  scheduler.py │ ──────────────► │     backup_manager.py    │   │
│   │  (Cron-like)  │                  │  mysqldump → ZIP → .enc  │   │
│   └──────────────┘                  └────────────┬─────────────┘   │
│         │                                         │                  │
│         │ also triggers                           ▼                  │
│         │                            ┌────────────────────────┐     │
│         ▼                            │     encryption.py      │     │
│   ┌──────────────────┐               │  AES-256 Fernet Key    │     │
│   │ anomaly_          │               └────────────┬───────────┘     │
│   │ detection.py     │                            │                  │
│   │ Isolation Forest │                            ▼                  │
│   └──────┬───────────┘               ┌────────────────────────┐     │
│          │                           │     cloud_upload.py    │     │
│          │ if anomaly found          │  Google Cloud Storage  │     │
│          ▼                           └────────────────────────┘     │
│   ┌──────────────────┐                                               │
│   │  alert_system.py │ ◄──── also triggered on backup failure       │
│   │  SMTP Email      │                                               │
│   └──────────────────┘                                               │
│                                                                       │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  app.py (Flask Dashboard) — Manual trigger + monitoring UI   │  │
│   └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Breakdown

```
┌─────────────────────────────────────────────────────────┐
│                    PROJECT MODULES                       │
├──────────────────┬──────────────────────────────────────┤
│  app.py          │  Flask admin dashboard. Provides UI  │
│                  │  to trigger backups, view logs, and  │
│                  │  monitor system health manually.     │
├──────────────────┼──────────────────────────────────────┤
│  backup_manager  │  Core engine. Runs mysqldump, ZIPs   │
│  .py             │  output, calls encryption, manages  │
│                  │  retention (auto-deletes > 7 days).  │
├──────────────────┼──────────────────────────────────────┤
│  encryption.py   │  Derives a Fernet key from password  │
│                  │  using PBKDF2. Encrypts .zip backup  │
│                  │  to .enc file (AES-256 equivalent).  │
├──────────────────┼──────────────────────────────────────┤
│  cloud_upload.py │  Uploads encrypted .enc files to    │
│                  │  Google Cloud Storage bucket via     │
│                  │  service account credentials.        │
├──────────────────┼──────────────────────────────────────┤
│  anomaly_        │  Isolation Forest ML model. Trains   │
│  detection.py    │  on historical DB metrics. Flags     │
│                  │  mass deletions or data injections.  │
├──────────────────┼──────────────────────────────────────┤
│  alert_system.py │  SMTP email service. Notifies admins │
│                  │  on failures, anomalies, or bad      │
│                  │  login attempts.                     │
├──────────────────┼──────────────────────────────────────┤
│  scheduler.py    │  Background runner using `schedule`. │
│                  │  Runs backup + anomaly pipeline      │
│                  │  daily without human intervention.   │
├──────────────────┼──────────────────────────────────────┤
│  setup_db.py     │  Initializes DB with dummy data and  │
│                  │  mocked historical metrics for ML    │
│                  │  model training.                     │
└──────────────────┴──────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
  MySQL Database
       │
       │  mysqldump
       ▼
  ┌─────────┐
  │ .sql    │  Raw SQL dump
  │  file   │
  └────┬────┘
       │  ZIP compression
       ▼
  ┌─────────┐
  │ .zip    │  Compressed archive
  │  file   │
  └────┬────┘
       │  AES-256 Fernet Encryption
       │  (key derived from .env password via PBKDF2)
       ▼
  ┌─────────┐
  │ .enc    │  Encrypted backup (stored locally)
  │  file   │
  └────┬────┘
       │
       ├──────────────────────────────────────────┐
       │  Local Storage                            │  Cloud Upload (optional)
       │  /backups/                                ▼
       │  (auto-purge after 7 days)    ┌─────────────────────────┐
       │                               │  Google Cloud Storage   │
       │                               │  Bucket (off-site DR)   │
       │                               └─────────────────────────┘
       │
  ┌────▼────────────────────────┐
  │  Anomaly Detection Pipeline │
  │                             │
  │  DB Metrics Collected:      │
  │  - table_size               │
  │  - row_count                │
  │                             │
  │  Isolation Forest Model     │
  │  predicts: NORMAL / ANOMALY │
  └────┬────────────────────────┘
       │
       │  If ANOMALY detected
       ▼
  ┌─────────────────┐
  │  alert_system   │
  │  → Email Admin  │
  └─────────────────┘
```

---

## 🧠 Anomaly Detection – How It Works

```
TRAINING PHASE (setup_db.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Historical Metrics  ──►  Isolation Forest  ──►  Trained Model (.pkl)
  (mocked: 90 days          (unsupervised ML          saved to disk
   of normal data)           algorithm)


INFERENCE PHASE (scheduler.py → anomaly_detection.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Live DB Metrics  ──►  Load Model  ──►  Predict
  (table_size,                              │
   row_count)                               ├── Score = NORMAL  ──► No action
                                            │
                                            └── Score = ANOMALY ──► Email Alert
                                                                     sent to Admin


WHAT IT DETECTS:
  ✅  Mass deletion attack (sudden row_count drop > threshold)
  ✅  Rapid data injection (sudden spike in table_size)
  ✅  Unusual DB growth patterns
```

---

## 🔐 Security Model

```
┌────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Layer 1: Credentials                                      │
│  ─────────────────────                                     │
│  All secrets stored in .env (never hardcoded)             │
│  • DB_PASSWORD                                             │
│  • BACKUP_ENCRYPTION_PASSWORD                              │
│  • SMTP credentials                                        │
│  • GCS service account key path                           │
│                                                            │
│  Layer 2: Encryption at Rest                               │
│  ────────────────────────────                              │
│  .zip → .enc using Fernet (AES-256-CBC + HMAC-SHA256)     │
│  Key derived via PBKDF2HMAC (100,000 iterations, SHA256)  │
│                                                            │
│  Layer 3: Cloud Off-site Storage                           │
│  ──────────────────────────────                            │
│  Encrypted backups pushed to GCS                          │
│  Service Account auth (least-privilege IAM role)          │
│                                                            │
│  Layer 4: Admin Dashboard Auth                             │
│  ─────────────────────────────                             │
│  Flask login with env-configured credentials              │
│  Failed login attempts trigger SMTP alert                 │
│                                                            │
│  Layer 5: AI Threat Detection                              │
│  ────────────────────────────                              │
│  Isolation Forest monitors DB metrics in real-time        │
│  Anomaly = immediate email alert to admin                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Category | Library / Tool |
|---|---|
| Language | Python 3.9+ |
| Web Framework | Flask |
| Database | MySQL + `mysql-connector-python` |
| Encryption | `cryptography` (Fernet / AES-256) |
| ML / AI | `scikit-learn` (Isolation Forest) |
| Scheduling | `schedule` |
| Cloud Storage | `google-cloud-storage` |
| Email Alerts | `smtplib` (SMTP) |
| Backup Utility | `mysqldump` (system binary) |

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.9+
- MySQL Server (`mysqldump` must be in system PATH)
- *(Optional)* Google Cloud Service Account JSON Key

### 2. Clone & Install

```bash
git clone https://github.com/rushi1808/Automated-DB-Backups.git
cd Automated-DB-Backups

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Open `.env` and update:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password       # ← change this
DB_NAME=backup_system_db

BACKUP_ENCRYPTION_PASSWORD=your_secret_key

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com        # ← change this
SMTP_PASSWORD=your_app_password       # ← use Google App Password

GCS_BUCKET_NAME=your-gcs-bucket       # ← optional
GCS_KEY_PATH=path/to/service_key.json # ← optional
```

> ⚠️ For Gmail SMTP, use an **App Password** (not your real password). Enable it at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### 4. Initialize Database

```bash
python setup_db.py
```

This creates the MySQL database, seeds dummy tables, and generates 90 days of mocked historical metrics for the Isolation Forest model to train on.

---

## 🚀 Running the System

The system has **two independent components** that run simultaneously:

### Component 1 — Web Dashboard

```bash
python app.py
```

Visit **http://localhost:5000**  
Login: `admin` / `admin` *(configurable in `.env`)*

**Dashboard features:**
- Manually trigger a backup
- View recent backup logs
- Monitor system health status
- View anomaly detection history

### Component 2 — Background Scheduler

Open a **new terminal**, activate the virtual environment, then:

```bash
python scheduler.py
```

This runs the full pipeline (backup + anomaly detection) automatically at the configured interval — no human intervention needed.

```
scheduler.py
    │
    ├── [Daily at configured time]
    │       ├── backup_manager.py  →  creates encrypted backup
    │       ├── cloud_upload.py    →  uploads to GCS (if configured)
    │       └── anomaly_detection.py → checks DB metrics, alerts if needed
    │
    └── [Continuous loop — runs forever until stopped]
```

---

## 📁 Project Structure

```
Automated-DB-Backups/
│
├── app.py                  # Flask dashboard
├── backup_manager.py       # Core backup logic
├── encryption.py           # AES-256 encryption
├── cloud_upload.py         # GCS upload
├── anomaly_detection.py    # Isolation Forest ML
├── alert_system.py         # SMTP email alerts
├── scheduler.py            # Automated pipeline runner
├── setup_db.py             # DB init & ML data seeding
├── data_classifier.py      # Data sensitivity classification
├── data_vault.py           # Secure vault operations
│
├── backups/                # Local encrypted backups
├── secure_vault/           # Vault storage
├── static/                 # Flask static assets
├── templates/              # Flask HTML templates
├── utils/                  # Helper utilities
│
├── .env                    # Configuration (secrets)
├── requirements.txt        # Python dependencies
└── system.log              # Application logs
```

---

## 🐛 Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `mysqldump not recognized` | Binary not in PATH | Add MySQL `bin/` folder to Windows Environment Variables Path (e.g., `C:\Program Files\MySQL\MySQL Server 8.0\bin`) |
| `Login invalid` | Wrong credentials in `.env` | Check `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`. Default is `admin`/`admin` |
| `Email failed` | Gmail blocked app access | Enable **App Passwords** in your Google Account (requires 2FA). Use the 16-character app password in `.env` |
| `GCS upload failed` | Missing/wrong key | Ensure `GCS_KEY_PATH` points to a valid service account JSON with `Storage Object Admin` role |
| `Anomaly model error` | DB not initialized | Run `python setup_db.py` first to seed historical metrics |

---

## 🎓 Viva Preparation — Key Concepts

| Question | One-line Answer |
|---|---|
| Why Isolation Forest? | Unsupervised; works without labelled attack data; efficient for tabular anomaly detection |
| Why Fernet over raw AES? | Fernet provides authenticated encryption (AES-256-CBC + HMAC-SHA256) — prevents tampering |
| Why PBKDF2 for key derivation? | Adds salt + 100k iterations, making brute-force of the encryption password computationally expensive |
| Why local + cloud backup? | Defense-in-depth: local = fast restore; cloud = disaster recovery if server is compromised |
| What triggers an email alert? | Backup failure, anomaly detected, or unauthorized dashboard login attempt |

---

## 📄 License

This project is developed as a **final year academic project**. Free to use for educational purposes.

---

<div align="center">
  Built with 🐍 Python · 🛡️ Security-first · 🤖 AI-powered
</div>
