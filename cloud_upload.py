import os
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger("cloud_upload")
load_dotenv()

def upload_to_gcs(local_file_path, destination_blob_name):
    """Uploads a file to Google Cloud Storage bucket."""
    credential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    bucket_name = os.getenv("GCS_BUCKET_NAME", "")

    if not credential_path or not os.path.exists(credential_path):
        logger.warning("GCS credentials not found or invalid. Skipping cloud upload. Set GOOGLE_APPLICATION_CREDENTIALS in .env.")
        return False

    if not bucket_name:
        logger.warning("GCS_BUCKET_NAME not set in .env. Skipping cloud upload.")
        return False

    try:
        # Initialize Google Cloud Storage Client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        logger.info(f"Uploading {local_file_path} to gs://{bucket_name}/{destination_blob_name}...")
        blob.upload_from_filename(local_file_path)
        
        logger.info("Upload complete!")
        return True
    except GoogleAPIError as e:
        logger.error(f"Failed to upload to GCS due to API error: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during GCS upload: {e}")
        return False
