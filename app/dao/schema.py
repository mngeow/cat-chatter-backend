from pydantic import BaseModel
from typing import Literal, List
from app.infrastructure.postgres.models import Chats as ChatORM

class BaseChatMessage(BaseModel):
    role: Literal["user","assistant","system"]
    content: str

class BaseChat(BaseModel):
    ...

class Chat(BaseChat):
    conversation_history: List[BaseChatMessage]
    description: str | None = None
    id: str

    @property
    def to_orm(self) -> ChatORM:
        return ChatORM(
            chat_id = self.id,
            conversation_history = [item.model_dump() for item in self.conversation_history],
            description=self.description
        )
    
    @classmethod
    def from_orm(cls, orm_obj: ChatORM):
       return cls(
            id = orm_obj.chat_id,
            conversation_history = [BaseChatMessage(**item) for item in orm_obj.conversation_history],
            description=orm_obj.description
        )