from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from datetime import datetime
from dotenv import load_dotenv

from utils.logger import setup_logger, LOG_FILE
from backup_manager import run_backup_process
from anomaly_detection import detect_anomalies
from data_vault import process_file_upload, process_link_submission, get_vault_history

logger = setup_logger("webapp")
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-if-missing")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    # Get backup history
    backups = []
    if os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            if os.path.isfile(os.path.join(BACKUP_DIR, f)):
                stat = os.stat(os.path.join(BACKUP_DIR, f))
                backups.append({
                    "name": f,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        backups.sort(key=lambda x: x["modified"], reverse=True)
        
    vault_items = get_vault_history()
        
    return render_template("index.html", backups=backups, vault=vault_items)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            logger.info(f"Successful login for user '{username}' from {request.remote_addr}")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.")
            logger.warning(f"Failed login attempt for user '{username}' from {request.remote_addr}")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/api/run_backup", methods=["POST"])
def run_backup():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    logger.info("Manual backup requested via API.")
    success = run_backup_process()
    if success:
        return jsonify({"status": "success", "message": "Backup completed successfully."})
    else:
        return jsonify({"status": "error", "message": "Backup failed. Check logs."}), 500

@app.route("/api/run_anomaly", methods=["POST"])
def run_anomaly():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    logger.info("Manual anomaly detection requested via API.")
    anomaly_detected = detect_anomalies()
    
    if anomaly_detected:
        return jsonify({"status": "warning", "message": "Anomaly Detected! Check logs and email alerts."})
    else:
        return jsonify({"status": "success", "message": "No anomalies detected. Database metrics are normal."})

@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    if 'vault_file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
        
    file = request.files['vault_file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
        
    # Save temp and process
    temp_path = os.path.join(BACKUP_DIR, file.filename)
    file.save(temp_path)
    
    result = process_file_upload(temp_path, file.filename)
    os.remove(temp_path) # cleanup temp
    
    return jsonify({"status": "success", "message": f"File stored. ML Sensitive: {result['sensitive']}. Encrypted: {result['encrypted']}"})

@app.route("/api/submit_link", methods=["POST"])
def submit_link():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    url = request.form.get("vault_link")
    if not url:
        return jsonify({"status": "error", "message": "No link provided"}), 400
        
    process_link_submission(url)
    return jsonify({"status": "success", "message": "Link saved to vault."})

@app.route("/api/logs")
def get_logs():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                return jsonify({"status": "success", "logs": "".join(lines[-100:])})  # Return last 100
        return jsonify({"status": "success", "logs": "No logs available yet."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask web dashboard server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
