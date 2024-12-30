from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

Base = declarative_base()

class Chats(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True)
    conversation_history = Column(JSONB, nullable=True)
    description = Column(String, nullable=True)
    persona_id = Column(String, ForeignKey('cat_personas.persona_id'), nullable=False)
    
    persona = relationship("CatPersonas", back_populates="chats")

class CatPersonas(Base):
    __tablename__ = "cat_personas"

    persona_id = Column(String, primary_key=True)
    definition = Column(JSONB)
    
    chats = relationship("Chats", back_populates="persona")