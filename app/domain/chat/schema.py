from pydantic import BaseModel
from app.dao.schema import Chat
from typing import List

class ListChatsResponse(BaseModel):
    chats: List[Chat]

class ChatBody(BaseModel):
    message: str