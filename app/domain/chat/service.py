from sqlalchemy.orm import scoped_session
from app.dao.chat import ChatDAO
from app.dao.schema import Chat, BaseChatMessage
from .schema import ListChatsResponse, ChatBody
from fastapi.responses import StreamingResponse
from openai import AzureOpenAI
from app.core.config import settings
from typing import Generator
from openai.types.chat import ChatCompletionChunk
from openai import Stream
from loguru import logger

class ChatService:
    def __init__(self, db_session: scoped_session) -> None:
        self._chat_dao = ChatDAO(db_session=db_session)

    def yield_chunks_gen(self, stream: Stream[ChatCompletionChunk], chat: Chat)->Generator:
        full_answer = ""
        for chunk in stream:
            chunk = chunk.choices[0].delta.content or ""
            yield chunk
            full_answer += chunk
        
        new_chat = chat.model_copy(deep=True)
        new_chat.conversation_history.append(BaseChatMessage(role='assistant',content=full_answer))
        self._chat_dao.update_chat(chat_obj=new_chat)

    
    def create_chat(self) -> Chat:
        return self._chat_dao.create_chat()
    
    def get_chats(self) -> ListChatsResponse:
        return ListChatsResponse(chats=self._chat_dao.fetch_all_chats())
    
    def get_chat_by_id(self, chat_id: str) -> Chat:
        return self._chat_dao.get_chat_by_id(chat_id=chat_id)
    
    def ask_question(self, payload: ChatBody, chat_id: str) -> StreamingResponse:

        chat_obj = self._chat_dao.get_chat_by_id(chat_id=chat_id)

        chat_obj.conversation_history.append(BaseChatMessage(role='user',content=payload.message))
        chat_obj.description = payload.message

        client = AzureOpenAI(
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY
        )

        stream = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            stream=True,
            messages=[item.model_dump() for item in chat_obj.conversation_history]

        )

        return StreamingResponse(
            content=self.yield_chunks_gen(stream=stream, chat=chat_obj),
            media_type="text/event-stream"
        )