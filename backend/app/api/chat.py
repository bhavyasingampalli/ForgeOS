from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.connection import Connection
from app.mcp.registry import mcp_registry
from app.utils.config import settings

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import tool

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_id: int
    message: str

@router.post("/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Get user connections
    connections = db.query(Connection).filter(
        Connection.user_id == request.user_id,
        Connection.status == 'Connected'
    ).all()
    
    connected_providers = [c.provider for c in connections]
    
    # 2. Get available tools dynamically based on connections
    available_tools_metadata = mcp_registry.get_tools_for_providers(connected_providers)
    
    # 3. Setup LangChain (Note: In a full MCP implementation, we'd bind actual Tool objects here)
    llm = ChatOpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")
    
    system_prompt = f"""
    You are ForgeOS, an AI Engineering Chief of Staff.
    The user has connected the following platforms: {', '.join(connected_providers) if connected_providers else 'None'}.
    You only have access to the capabilities of these connected platforms.
    Available Tools: {available_tools_metadata}
    
    If the user asks to do something on a platform they haven't connected, gracefully tell them they need to connect it first from Settings.
    Before executing any tool, you must ask the user for permission. Show them an execution plan.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=request.message)
    ]
    
    response = llm.invoke(messages)
    
    return {
        "reply": response.content,
        "tools_exposed": available_tools_metadata,
        "connected_platforms": connected_providers
    }
