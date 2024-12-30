from fastapi import APIRouter
from app.routes.endpoints.chat import router as chat_router
from app.routes.endpoints.persona import router as persona_router

api_router = APIRouter(prefix="/api")

api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(persona_router, prefix="/persona")