import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger("encryption")

# Load environment variables
load_dotenv()

# Set up a secure key derivation
def _get_fernet_key():
    secret = os.getenv("SECRET_KEY", "fallback-secret-if-missing")
    salt = b'secure-salt-value-123'  # Hardcoded salt for consistency across restarts
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return key

key = _get_fernet_key()
fernet = Fernet(key)

def encrypt_file(file_path):
    """Encrypts a file and returns the encrypted file path (.enc)."""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found for encryption: {file_path}")
            return None

        with open(file_path, "rb") as file:
            original = file.read()

        encrypted = fernet.encrypt(original)
        
        encrypted_path = file_path + ".enc"
        with open(encrypted_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted)
            
        logger.info(f"Successfully encrypted file to {encrypted_path}")
        return encrypted_path
    except Exception as e:
        logger.error(f"Encryption failed for {file_path}: {e}")
        return None

def decrypt_file(encrypted_path, output_path):
    """Decrypts an encrypted file back to its original format."""
    try:
        with open(encrypted_path, "rb") as enc_file:
            encrypted = enc_file.read()

        decrypted = fernet.decrypt(encrypted)

        with open(output_path, "wb") as dec_file:
            dec_file.write(decrypted)
            
        logger.info(f"Successfully decrypted file to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Decryption failed for {encrypted_path}: {e}")
        return None
