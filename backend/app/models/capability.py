from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime
from app.db.database import Base

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g. "GitHub"
    
    capabilities = relationship("Capability", back_populates="provider")

class Capability(Base):
    __tablename__ = "capabilities"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String, index=True) # e.g. "Repository"
    
    provider = relationship("Provider", back_populates="capabilities")
    tools = relationship("Tool", back_populates="capability")

class Tool(Base):
    __tablename__ = "tools"
    id = Column(Integer, primary_key=True, index=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id"))
    name = Column(String) # e.g. "Repository MCP"
    version = Column(String)
    
    capability = relationship("Capability", back_populates="tools")
    operations = relationship("Operation", back_populates="tool")

class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    name = Column(String) # e.g. "create_repository"
    description = Column(String)
    schema_hash = Column(String)
    last_discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tool = relationship("Tool", back_populates="operations")
