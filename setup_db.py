import mysql.connector
import os
from dotenv import load_dotenv
import random
from utils.logger import setup_logger

logger = setup_logger("setup_db")
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "demo_company")

def setup_database():
    try:
        # Connect without specific database to create it if it doesn't exist
        logger.info(f"Connecting to MySQL at {DB_HOST} with user {DB_USER}...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create the database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        logger.info(f"Database {DB_NAME} created or already exists.")

        # Connect to the new database
        conn.database = DB_NAME

        # Create dummy application table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Table 'users' created.")

        # Insert some dummy users if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            for i in range(1, 101):
                cursor.execute(
                    "INSERT INTO users (username, email) VALUES (%s, %s)",
                    (f"user_{i}", f"user{i}@example.com")
                )
            conn.commit()
            logger.info("Inserted 100 dummy users.")

        # Create metrics table for Anomaly Detection ML model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                backup_date DATE NOT NULL,
                db_size_mb FLOAT NOT NULL,
                row_count INT NOT NULL
            )
        """)
        logger.info("Table 'backup_metrics' created.")

        # Insert historical data for ML model simulation (30 days of data)
        cursor.execute("SELECT COUNT(*) FROM backup_metrics")
        if cursor.fetchone()[0] == 0:
            from datetime import datetime, timedelta
            today = datetime.now()
            
            base_size = 50.0 # MB
            base_rows = 5000
            
            for i in range(30, -1, -1):
                record_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                
                # Introduce natural variation
                current_size = base_size + random.uniform(-2, 2)
                current_rows = base_rows + random.randint(10, 50)
                
                # Introduce Anomaly exactly 5 days ago (drop anomaly)
                if i == 5:
                    current_size = 5.0  # Massive sudden drop in backup size
                    current_rows = 500  # Massive sudden drop in rows
                    
                cursor.execute(
                    "INSERT INTO backup_metrics (backup_date, db_size_mb, row_count) VALUES (%s, %s, %s)",
                    (record_date, current_size, current_rows)
                )
                
                # Increment the base slightly for organic growth
                base_size += random.uniform(0.1, 0.5)
                base_rows += random.randint(10, 50)

            conn.commit()
            logger.info("Inserted 30 days of mocked historical metrics for Anomaly Detection.")

        # Create table for secure data vault uploads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                is_sensitive BOOLEAN NOT NULL DEFAULT 0,
                is_encrypted BOOLEAN NOT NULL DEFAULT 0,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Table 'uploaded_data' created.")

        cursor.close()
        conn.close()
        logger.info("Database Setup Complete.")

    except mysql.connector.Error as err:
        logger.error(f"MySQL Error: {err}")
    except Exception as e:
        logger.error(f"Error setting up dummy database: {e}")

if __name__ == "__main__":
    setup_database()
