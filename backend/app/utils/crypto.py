from cryptography.fernet import Fernet
import os
from typing import Optional
from app.utils.config import settings

class CryptoService:
    def __init__(self):
        # We allow a fallback for testing, but in production this should be strictly enforced
        key = getattr(settings, 'MASTER_ENCRYPTION_KEY', None)
        if not key:
            # Fallback for dev environments if not set in .env
            key = Fernet.generate_key().decode()
            
        # Ensure the key is bytes
        if isinstance(key, str):
            self.fernet = Fernet(key.encode('utf-8'))
        else:
            self.fernet = Fernet(key)

    def encrypt_token(self, token: str) -> Optional[str]:
        if not token:
            return None
        # Fernet returns bytes, store as string
        return self.fernet.encrypt(token.encode('utf-8')).decode('utf-8')

    def decrypt_token(self, encrypted_token: str) -> Optional[str]:
        if not encrypted_token:
            return None
        # Fernet expects bytes, returns bytes
        return self.fernet.decrypt(encrypted_token.encode('utf-8')).decode('utf-8')

crypto_service = CryptoService()
