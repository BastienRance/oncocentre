"""
Encryption utilities for sensitive patient data
"""

from cryptography.fernet import Fernet
import os

def get_encryption_key():
    """Get or create encryption key for database fields"""
    key_path = 'encryption.key'
    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        return key

# Initialize encryption
ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """Encrypt sensitive data"""
    if isinstance(data, str):
        return cipher_suite.encrypt(data.encode()).decode()
    return cipher_suite.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()