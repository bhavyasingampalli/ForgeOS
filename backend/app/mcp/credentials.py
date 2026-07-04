from sqlalchemy.orm import Session
from app.models.connection import WorkspaceConnection, Credential
from app.utils.crypto import crypto_service

class CredentialManager:
    def __init__(self, db: Session):
        self.db = db

    def get_temporary_credential(self, user_id: int, provider: str) -> str:
        """
        Retrieves the encrypted credential for the user and provider,
        decrypts it temporarily, and returns the plaintext token.
        The plaintext token is never stored and should be discarded
        by the caller immediately after use.
        """
        connection = self.db.query(WorkspaceConnection).filter(
            WorkspaceConnection.user_id == user_id,
            WorkspaceConnection.provider == provider,
            WorkspaceConnection.status == 'CONNECTED'
        ).first()

        if not connection or not connection.credential:
            raise ValueError(f"No active credential found for {provider}")

        encrypted_token = connection.credential.encrypted_access_token
        decrypted_token = crypto_service.decrypt_token(encrypted_token)
        
        if not decrypted_token:
            raise ValueError(f"Failed to decrypt credential for {provider}")
            
        return decrypted_token
