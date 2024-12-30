from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from app.routes.servicesfac import get_chat_service
from fastapi import Depends
from app.domain.chat.service import ChatService
from app.dao.schema import Chat
from app.domain.chat.schema import ListChatsResponse, ChatBody
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods="*",
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat API"}

@app.put("/api/chat/{chat_id}")
def ask_question(
    chat_id: str,
    body: ChatBody,
    chat_service: ChatService = Depends(get_chat_service)
)->StreamingResponse:
    return chat_service.ask_question(payload=body, chat_id=chat_id)

@app.get("/api/chat/{chat_id}")
def get_chat_by_id(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> Chat:
    return chat_service.get_chat_by_id(chat_id=chat_id)

@app.post("/api/chat")
def create_chat(
    chat_service: ChatService = Depends(get_chat_service)
) -> Chat:
    return chat_service.create_chat()

@app.get("/api/chats")
def get_chats(
    chat_service: ChatService = Depends(get_chat_service)
) -> ListChatsResponse:
    return chat_service.get_chats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
