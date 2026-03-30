# Intelligent Secure Automated Database Backup & Anomaly Detection System

A production-level Python final year project automating MySQL database backups with AES-256 encryption, Google Cloud Storage integration, and AI-powered Anomaly Detection.

## Project Architecture & Modules (For Viva Explanation)

1. **`app.py`**: A Flask Web Server providing an Admin Dashboard to trigger backups, monitor system health, and view logs manually.
2. **`backup_manager.py`**: The core component that handles the `mysqldump` command, compresses the resulting SQL file into a ZIP archive, delegates encryption, and manages local backup retention (e.g., deletes backups older than 7 days).
3. **`encryption.py`**: Utilizes the `cryptography` library to derive a secure Fernet key (AES-256 equivalent) from a secret password and encrypts the `.zip` backup before archiving. Ensures data security at rest.
4. **`cloud_upload.py`**: Interfaces with the Google Cloud Storage API to optionally upload the encrypted backups off-site for disaster recovery.
5. **`anomaly_detection.py`**: An AI module utilizing Scikit-Learn's **Isolation Forest** algorithm. It continuously analyzes historical database metrics (like table size and row count) to identify sudden, massive drops or spikes which could indicate a malicious mass-deletion attack or rapid data injection.
6. **`alert_system.py`**: An SMTP alerting service that triggers warning emails to admins upon backup failures, anomaly detection, or unauthorized login attempts.
7. **`scheduler.py`**: A background automation script utilizing `schedule` to run the backup + anomaly detection pipeline daily without human intervention.
8. **`setup_db.py`**: A helper script to initialize the project database with dummy user data and simulate historical metrics for the AI model to learn from.

## Step-by-Step Setup Guide

### 1. Prerequisites
- Python 3.9+
- MySQL Server (Ensure `mysqldump` is in your system PATH)
- (Optional) Google Cloud Service Account JSON Key

### 2. Installation
1. Clone this repository or open the folder in an IDE (like VS Code).
2. Create a virtual environment:
   ```bash
   
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Database Setup & Configuration
1. Open the `.env` file. Change `DB_PASSWORD` to your local MySQL root password.
2. Configure `SMTP_USER` and `SMTP_PASSWORD` if you want email alerts (Use Google App Passwords, not your real password!).
3. Run the database setup script to create the database, dummy tables, and mocked historical metrics for ML:
   ```bash
   python setup_db.py
   ```

### 4. Running the System
You have two components to run:

**A. Start the Web Dashboard:**
```bash
python app.py
```
*Visit `http://localhost:5000` in your browser. Login with username `admin` and password `admin`.*

**B. Start the Automated Background Scheduler:**
Open a *new* terminal window, activate the virtual environment, and run:
```bash
python scheduler.py
```
*This will run the automated backup and anomaly detection sequence continuously in the background at the specified time interval.*

## Common Issues & Troubleshooting
- **`mysqldump` command not recognized**: You must add your MySQL `bin` folder (e.g., `C:\Program Files\MySQL\MySQL Server 8.0\bin`) to your Windows Environment Variables Path.
- **Login invalid**: Check your `.env` for `ADMIN_USERNAME` and `ADMIN_PASSWORD`. By default, both are `admin`.
- **Email Failed**: Gmail requires "App Passwords" to be enabled if you have 2FA on your Google Account. Regular passwords will fail.
