from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
import datetime
from app.db.database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String)
    capability = Column(String)
    tool = Column(String)
    operation = Column(String)
    execution_id = Column(String, index=True)
    provider = Column(String)
    latency_ms = Column(Float)
    status = Column(String)
    error = Column(String, nullable=True)
    correlation_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ExecutionEvent(Base):
    __tablename__ = "execution_events"
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False) 
    # e.g. "LLM Planned", "Capability Matched", "Authorization Checked", "Credential Loaded", "MCP Invoked", "Response Received", "Completed"
    payload = Column(String, nullable=True) # JSON payload of the event state
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
