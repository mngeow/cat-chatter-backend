from app.domain.chat.service import ChatService
from app.infrastructure.postgres.session import get_session
from fastapi import Depends
from sqlalchemy.orm import scoped_session
from app.domain.persona.service import PersonaService

def get_chat_service(db_session: scoped_session = Depends(get_session)) -> ChatService:
    return ChatService(db_session=db_session)

def get_persona_service(db_session: scoped_session = Depends(get_session)) -> PersonaService:
    return PersonaService(db_session=db_session)