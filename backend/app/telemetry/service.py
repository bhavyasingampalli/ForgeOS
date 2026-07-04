import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.audit import ExecutionEvent, AuditEvent

# Create a local websocket manager or import the global one
# For now, to avoid circular imports we will dynamically import ws_manager when broadcasting
class TelemetryService:
    def __init__(self):
        pass

    async def record_execution_event(
        self, 
        execution_id: str, 
        event_type: str, 
        payload: Optional[Dict] = None
    ):
        """Records an orchestration timeline event."""
        db = SessionLocal()
        try:
            event = ExecutionEvent(
                execution_id=execution_id,
                event_type=event_type,
                payload=json.dumps(payload) if payload else None
            )
            db.add(event)
            db.commit()
        finally:
            db.close()
            
        # Broadcast to UI Activity Stream
        from app.mcp.orchestrator import ws_manager
        
        await ws_manager.broadcast({
            "execution_id": execution_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def record_audit_event(
        self,
        user_id: int,
        session_id: str,
        capability: str,
        tool: str,
        operation: str,
        execution_id: str,
        provider: str,
        status: str,
        latency_ms: float = 0.0,
        error: str = None
    ):
        """Records a granular audit analytics event."""
        db = SessionLocal()
        try:
            audit = AuditEvent(
                user_id=user_id,
                session_id=session_id,
                capability=capability,
                tool=tool,
                operation=operation,
                execution_id=execution_id,
                provider=provider,
                latency_ms=latency_ms,
                status=status,
                error=error,
                correlation_id=str(uuid.uuid4())
            )
            db.add(audit)
            db.commit()
        finally:
            db.close()

telemetry_service = TelemetryService()
