from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.db.database import Base

class WorkspaceConnection(Base):
    __tablename__ = "workspace_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String, index=True, nullable=False) # 'Google', 'GitHub', 'Slack', 'Notion'
    status = Column(String, default="NOT_CONNECTED") # NOT_CONNECTED, AUTHORIZING, CONNECTING, DISCOVERING, CONNECTED, UNHEALTHY, FAILED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="workspace_connections")
    credential = relationship("Credential", back_populates="connection", uselist=False)

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("workspace_connections.id"), unique=True)
    encrypted_access_token = Column(String, nullable=False)
    encrypted_refresh_token = Column(String)
    expires_at = Column(DateTime)
    scope = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    connection = relationship("WorkspaceConnection", back_populates="credential")
