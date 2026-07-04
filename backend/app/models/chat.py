from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from app.db.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")
