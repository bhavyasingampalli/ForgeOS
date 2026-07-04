from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db
from app.utils.config import settings
from app.authentication import auth
from app.integration import oauth
from app.mcp.manager import MCPManager
from app.domain.ai_planning_engine import AIPlanningEngine
from app.domain.execution_engine import ExecutionEngine
from app.domain.approval_manager import ApprovalManager
from app.mcp.orchestrator import MCPOrchestrator, ws_manager

# Import models so Base metadata has them registered
import app.models.identity
import app.models.connection
import app.models.capability
import app.models.audit
import app.models.chat


app = FastAPI(title="ForgeOS Command Center API")

# Configure CORS for HttpOnly cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth.router)
app.include_router(oauth.router)

# Initialize core engines
planning_engine = AIPlanningEngine()
execution_engine = ExecutionEngine()
approval_manager = ApprovalManager()

class RequestPrompt(BaseModel):
    user_id: int
    prompt: str

from app.models.chat import ChatSession, Message

@app.post("/api/plan")
async def create_plan(req: RequestPrompt, db: Session = Depends(get_db)):
    mcp_manager = MCPManager(db)
    
    # 0. Load Chat History
    # For demo simplicity, get the latest active session for this user or create one
    chat_session = db.query(ChatSession).filter(ChatSession.user_id == req.user_id).order_by(ChatSession.id.desc()).first()
    if not chat_session:
        chat_session = ChatSession(user_id=req.user_id)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        
    # Get last 10 messages for context (latest first, then reverse for chronological order)
    db_messages = db.query(Message).filter(Message.session_id == chat_session.id).order_by(Message.id.desc()).limit(10).all()
    chat_history = [(msg.role, msg.content) for msg in reversed(db_messages)]
    
    # 1. Discover authenticated tools via MCP Manager
    available_capabilities, _ = await mcp_manager.discover_available_capabilities(req.user_id)
    
    # 2. Planning Engine (LangChain) determines intent
    intent = planning_engine.generate_plan(req.prompt, available_capabilities, chat_history=chat_history)
    
    # Save the new exchange to DB
    user_msg = Message(session_id=chat_session.id, role="user", content=req.prompt)
    ai_msg = Message(session_id=chat_session.id, role="assistant", content=intent.message)
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()
    
    # 3. Execution Engine generates a deterministic plan preview
    plan = execution_engine.generate_execution_plan(intent)
    
    # 4. Approval Manager stages the plan and waits for user confirmation
    # We use a mocked session ID here for the demo
    session_id = f"sess_{req.user_id}_1"
    approval_preview = approval_manager.request_approval(session_id, plan)
    
    return approval_preview

@app.post("/api/execute/{session_id}")
async def execute_plan(session_id: str, db: Session = Depends(get_db)):
    mcp_manager = MCPManager(db)
    orchestrator = MCPOrchestrator(mcp_manager)
    
    # 1. Approve the plan
    approved_plan = approval_manager.approve(session_id)
    
    if not approved_plan:
        raise HTTPException(status_code=404, detail="No pending plan found for this session")
        
    # 2. Execute via MCP Orchestrator
    results = await orchestrator.execute_plan(approved_plan)
    
    return {"status": "Success", "results": results}

@app.get("/api/capabilities")
async def get_capabilities(user_id: int = 1, db: Session = Depends(get_db)):
    mcp_manager = MCPManager(db)
    capabilities, metadata = await mcp_manager.discover_available_capabilities(user_id)
    return {"capabilities": capabilities, "metadata": metadata}

@app.websocket("/api/ws/activity")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # We don't expect the client to send much, just keep it alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"message": "Welcome to ForgeOS Backend (MCP-Native)"}
