import schedule
import time
from utils.logger import setup_logger
from backup_manager import run_backup_process
from anomaly_detection import detect_anomalies

logger = setup_logger("scheduler")

def daily_job():
    """Runs the backup and anomaly detection sequence."""
    logger.info("Executing scheduled cron job...")
    
    # 1. Take Backup
    backup_result = run_backup_process()
    
    if backup_result:
        # 2. If backup successful, analyze the DB metrics to simulate Anomaly Detection
        # In a real app, backup_manager would log metrics to the DB, which we simulate here.
        # But here detect_anomalies will read from our mocked setup_db.py metrics.
        detect_anomalies()
    else:
        logger.error("Skipping Anomaly Detection as Backup Process failed.")

def start_scheduler():
    # Schedule job every day at 02:00 AM
    schedule.every().day.at("02:00").do(daily_job)

    # For testing: Run every 1 minute
    # schedule.every(1).minutes.do(daily_job)
    
    logger.info("Scheduler started. Waiting for next job execution...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler manually stopped.")

if __name__ == "__main__":
    start_scheduler()
