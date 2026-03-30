import os
import shutil
import mysql.connector
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from utils.logger import setup_logger
from data_classifier import predict_sensitivity
from encryption import encrypt_file

logger = setup_logger("data_vault")
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "demo_company")

VAULT_DIR = os.getenv("VAULT_DIR", "secure_vault")
if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

def _get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
    except Exception as e:
        logger.error(f"Vault DB Connection failed: {e}")
        return None

def process_file_upload(temp_file_path, original_filename):
    """
    Reads the file, runs ML model to detect sensitivity,
    encrypts it if sensitive, and logs to MySQL database.
    """
    safe_filename = secure_filename(original_filename)
    final_path = os.path.join(VAULT_DIR, safe_filename)
    
    # Check if text-based file to read contents
    content = ""
    if safe_filename.endswith('.txt') or safe_filename.endswith('.csv'):
        try:
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            pass # Ignore read errors for binary files
            
    # Move temp file to vault initially
    shutil.copy(temp_file_path, final_path)
    
    # ML Prediction
    is_sensitive = False
    if content:
        is_sensitive = predict_sensitivity(content)
        
    # Auto-Encrypt if sensitive
    is_encrypted = False
    if is_sensitive:
        logger.warning(f"ML classified {safe_filename} as SENSITIVE! Auto-encrypting vault data.")
        encrypted_path = encrypt_file(final_path)
        if encrypted_path:
            os.remove(final_path) # Remove unencrypted
            safe_filename += ".enc"
            is_encrypted = True
            
    # Database Logging
    conn = _get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO uploaded_data (filename, file_type, is_sensitive, is_encrypted) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (safe_filename, "file", is_sensitive, is_encrypted))
            conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error saving to uploaded_data: {e}")
        finally:
            conn.close()
            
    return {"filename": safe_filename, "sensitive": is_sensitive, "encrypted": is_encrypted}

def process_link_submission(url):
    """
    Logs a submitted link into the database vault.
    Links are inherently not encrypted files, but tracked.
    """
    # Simply log URL as a 'link' file_type. Real system might add URL scan here.
    conn = _get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO uploaded_data (filename, file_type, is_sensitive, is_encrypted) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (url, "link", False, False))
            conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error saving link to DB: {e}")
        finally:
            conn.close()
            
    logger.info(f"Link added to vault: {url}")
    return {"url": url, "status": "stored"}

def get_vault_history():
    """Fetches uploaded data history from the database."""
    history = []
    conn = _get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM uploaded_data ORDER BY upload_date DESC")
            history = cursor.fetchall()
            cursor.close()
        except Exception as e:
            logger.error(f"Error fetching vault history: {e}")
        finally:
            conn.close()
    return history
