import mysql.connector
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from dotenv import load_dotenv

from utils.logger import setup_logger
from alert_system import trigger_anomaly_alert

logger = setup_logger("anomaly_detection")
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "demo_company")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MySQL for Anomaly Detection: {err}")
        return None

def fetch_historical_metrics():
    """Fetches historical backup metrics from MySQL to train the ML Model."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        query = "SELECT backup_date, db_size_mb, row_count FROM backup_metrics ORDER BY backup_date ASC"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        logger.error(f"Error reading metrics from DB: {e}")
        return None
    finally:
        conn.close()

def detect_anomalies():
    """Runs Isolation Forest algorithm to detect data spikes/drops."""
    logger.info("Initializing Anomaly Detection sequence...")
    df = fetch_historical_metrics()
    
    if df is None or df.empty:
        logger.warning("No historical metrics found for training.")
        return False

    if len(df) < 5:
        logger.warning("Not enough data to run anomaly detection reliably (minimum 5 days required).")
        return False

    # Features: db_size_mb and row_count
    # Using Isolation Forest for outlier detection
    X = df[['db_size_mb', 'row_count']]
    
    # contamination = 0.05 implies we expect ~5% of data points to be outliers
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    
    # Predict (-1 is anomaly, 1 is normal)
    predictions = model.predict(X)
    df['anomaly'] = predictions
    
    # Check the MOST RECENT entry.
    latest_entry = df.iloc[-1]
    
    if latest_entry['anomaly'] == -1:
        logger.warning(f"ANOMALY DETECTED on latest backup! Date: {latest_entry['backup_date']}, Size: {latest_entry['db_size_mb']}MB, Rows: {latest_entry['row_count']}")
        trigger_anomaly_alert(
            f"Anomalous metric recognized.\n"
            f"Date: {latest_entry['backup_date']}\n"
            f"Size: {latest_entry['db_size_mb']} MB\n"
            f"Rows: {latest_entry['row_count']}\n"
            f"This could indicate accidental mass-deletion or an unauthorized mass-insertion attack."
        )
        return True
    
    logger.info("Latest metrics are normal. No anomalies detected.")
    return False

if __name__ == "__main__":
    detect_anomalies()
