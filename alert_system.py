import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger("alert_system")
load_dotenv()

def send_alert_email(subject, body):
    """Sends an email alert for critical system events."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "587")
    sender_email = os.getenv("SMTP_USER", "")
    sender_password = os.getenv("SMTP_PASSWORD", "")
    receiver_email = sender_email # Self-alerting by default

    if not all([smtp_host, smtp_port, sender_email, sender_password]):
        logger.warning(f"Email credentials not fully configured. Email skipped. Content was: {subject} - {body}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Setup server
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        logger.info(f"Alert email sent successfully to {receiver_email}. Subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send alert email. Make sure App Passwords are used. Error: {e}")
        return False

# Usage wrapper for specific alerts
def trigger_backup_failure_alert(error_detail):
    send_alert_email("[CRITICAL] Database Backup Failed", f"A recent automated backup failed.\n\nError details:\n{error_detail}")

def trigger_anomaly_alert(detail_message):
    send_alert_email("[WARNING] Database Anomaly Detected", f"An anomaly was detected in the database metrics.\n\nDetails:\n{detail_message}")

def trigger_security_alert(ip_address, event_detail):
    send_alert_email("[SECURITY WARNING] Unauthorized Access Attempt", f"Security violation detected from IP {ip_address}.\n\nDetails: {event_detail}")
