from fastapi import APIRouter
from app.routes.servicesfac import get_chat_service
from fastapi import Depends
from app.domain.chat.service import ChatService
from app.dao.schema import Chat
from app.domain.chat.schema import ListChatsResponse, ChatBody
from fastapi.responses import StreamingResponse


router = APIRouter()

@router.put("/{chat_id}")
def ask_question(
    chat_id: str,
    body: ChatBody,
    chat_service: ChatService = Depends(get_chat_service)
)->StreamingResponse:
    return chat_service.ask_question(payload=body, chat_id=chat_id)

@router.get("/{chat_id}")
def get_chat_by_id(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> Chat:
    return chat_service.get_chat_by_id(chat_id=chat_id)

@router.post("")
def create_chat(
    chat_service: ChatService = Depends(get_chat_service)
) -> Chat:
    return chat_service.create_chat()

@router.get("")
def get_chats(
    chat_service: ChatService = Depends(get_chat_service)
) -> ListChatsResponse:
    return chat_service.get_chats()