import os
import subprocess
import time
from datetime import datetime
import zipfile
from dotenv import load_dotenv

from utils.logger import setup_logger
from encryption import encrypt_file
from cloud_upload import upload_to_gcs
from alert_system import trigger_backup_failure_alert

logger = setup_logger("backup_manager")
load_dotenv()

# MySQL Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "demo_company")
DB_PORT = os.getenv("DB_PORT", "3306")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 7))

# Ensure backup directory exists
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def generate_mysql_dump(backup_file_path):
    """Executes mysqldump to backup the database."""
    # Build mysqldump command
    # NOTE: mysqldump must be in the system PATH.
    dump_cmd = [
        "mysqldump",
        f"-h{DB_HOST}",
        f"-P{DB_PORT}",
        f"-u{DB_USER}",
        f"-p{DB_PASSWORD}",
        DB_NAME
    ]
    try:
        logger.info(f"Starting database dump for {DB_NAME}...")
        with open(backup_file_path, 'w', encoding='utf-8') as outfile:
            process = subprocess.Popen(dump_cmd, stdout=outfile)
            process.wait()

        if process.returncode != 0:
            raise Exception("mysqldump command failed.")
        return True
    except FileNotFoundError:
        error_msg = "'mysqldump' command not found. Ensure MySQL Server is installed and added to PATH."
        logger.error(error_msg)
        trigger_backup_failure_alert(error_msg)
        return False
    except Exception as e:
        logger.error(f"Error during mysql dump: {e}")
        trigger_backup_failure_alert(str(e))
        return False

def zip_file(source_path, zip_path):
    """Compresses the SQL dump into a ZIP file."""
    try:
        logger.info(f"Compressing dump into {zip_path}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(source_path, os.path.basename(source_path))
        return True
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        return False

def clean_old_backups():
    """Removes backups older than RETENTION_DAYS."""
    now = time.time()
    for f in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, f)
        if os.path.isfile(file_path):
            if os.stat(file_path).st_mtime < now - RETENTION_DAYS * 86400:
                os.remove(file_path)
                logger.info(f"Deleted old backup: {file_path}")

def run_backup_process():
    """Main backup orchestration function."""
    logger.info("--- Automated Backup Process Initiated ---")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sql_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.sql")
    zip_file_path = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{timestamp}.zip")

    # Step 1: Dump
    success = generate_mysql_dump(sql_file)
    if not success:
        return False

    # Step 2: Zip
    if zip_file(sql_file, zip_file_path):
        os.remove(sql_file)  # Clean up uncompressed SQL
        
        # Step 3: Encrypt
        encrypted_file = encrypt_file(zip_file_path)
        if encrypted_file:
            os.remove(zip_file_path)  # Clean up unencrypted zip
            
            # Step 4: Upload to GCS
            upload_to_gcs(encrypted_file, os.path.basename(encrypted_file))
            
            # Step 5: Clean old versions locally
            clean_old_backups()
            logger.info("--- Automated Backup Process Completed Successfully ---")
            return True
        else:
            trigger_backup_failure_alert("Encryption failed. Backup incomplete.")
    else:
        trigger_backup_failure_alert("Compression failed. Backup incomplete.")
    
    logger.error("--- Automated Backup Process Failed ---")
    return False

if __name__ == "__main__":
    run_backup_process()
