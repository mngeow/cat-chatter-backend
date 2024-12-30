from sqlalchemy.orm import scoped_session
from sqlalchemy import select, update
from .schema import Chat, BaseChatMessage
from app.infrastructure.postgres.models import Chats as ChatORM
import uuid
from typing import List

class ChatDAO:
    def __init__(self, db_session: scoped_session) -> None:
        self._db_session = db_session
    
    def create_chat(self) -> Chat:
        chat_obj = Chat(
            id = str(uuid.uuid4()),
            conversation_history=[]
        )

        orm_obj = chat_obj.to_orm

        self._db_session.add(orm_obj)
        self._db_session.flush()
        self._db_session.refresh(orm_obj)

        return Chat.from_orm(orm_obj=orm_obj)
    
    def fetch_all_chats(self) -> List[Chat]:
        stmt = select(ChatORM)
        result_proxy = self._db_session.execute(stmt)
        res = result_proxy.scalars().all()

        return [Chat.from_orm(orm_obj=item) for item in res]
    
    def get_chat_by_id(self, chat_id: str) -> Chat:
        stmt = select(ChatORM).filter_by(chat_id=chat_id)
        result_proxy = self._db_session.execute(stmt)
        res = result_proxy.scalars().first()

        return Chat.from_orm(orm_obj=res)
    
    def update_chat(self, chat_obj: Chat) -> None:
        stmt = update(ChatORM).where(ChatORM.chat_id == chat_obj.id).values(conversation_history=[item.model_dump() for item in chat_obj.conversation_history],description=chat_obj.description)
        self._db_session.execute(stmt)
        self._db_session.commit()