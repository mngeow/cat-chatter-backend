from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Chats(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True)
    conversation_history = Column(JSONB, nullable=True)
    description = Column(String, nullable=True)