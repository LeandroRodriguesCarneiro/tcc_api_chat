from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from fastapi.security import OAuth2PasswordBearer

from ....services import ChatService, SecurityService
from ....database import Database
from ....schemas import (
    ChatStartRequest,
    ChatSendRequest,
)
from ....loggin import logger

database = Database.get_instance()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatController:
    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route("/message", self.send_message, methods=["POST"])
        self.router.add_api_route("/history", self.get_user_history, methods=["GET"])
        self.router.add_api_route("/history/{conversation_id}", self.get_conversation_history, methods=["GET"])

    def validate_token(self, access_token: str):
        if not access_token:
            raise HTTPException(status_code=401, detail="Usuário não autenticado")

        security = SecurityService()
        try:
            security.validate_access_token(access_token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    async def send_message(
        self,
        data: ChatStartRequest = Body(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(Database.get_db)
    ):
        self.validate_token(token)
        service = ChatService(db)

        try:
            if data.conversation_id:
                conversation = service.get_conversation(data.conversation_id)
                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversa não encontrada")

                service.add_message(data.conversation_id, "user", data.message)
                response = service.generate_response(data.conversation_id, data.message)
                service.add_message(data.conversation_id, "assistant", response)

                return {
                    "status": "success",
                    "conversation_id": data.conversation_id,
                    "response": response,
                    "role": "assistant",
                    "timestamp": datetime.now(timezone.utc)
                }

            new_conversation = service.create_conversation(token)
            service.add_message(new_conversation.id, "user", data.message)

            response = service.generate_response(new_conversation.id, data.message)
            service.add_message(new_conversation.id, "assistant", response)

            return {
                    "status": "success",
                    "conversation_id": data.conversation_id,
                    "response": response,
                    "role": "assistant",
                    "timestamp": datetime.now(timezone.utc)
                }

        except Exception as e:
            logger.error(f"Erro ao iniciar conversa: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno no servidor")

    async def get_user_history(
        self,
        token: str = Depends(oauth2_scheme),
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(Database.get_db)
    ):
        self.validate_token(token)
        service = ChatService(db)

        try:
            conversations = service.get_user_conversations(token, limit=limit)

            history = [{
                "conversation_id": conv.id,
                "title": conv.title or "Nova conversa",
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "last_message_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": conv.message_count or 0
            } for conv in conversations]

            return {
                "status": "success",
                "conversations": history
            }

        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno no servidor")

    async def get_conversation_history(
        self,
        conversation_id: str,
        token: str = Depends(oauth2_scheme),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(Database.get_db)
    ):
        self.validate_token(token)
        service = ChatService(db)

        try:
            conversation = service.get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")

            messages = service.get_conversation_messages(conversation_id, limit=limit)

            history = [{
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            } for msg in messages]

            return {
                "status": "success",
                "conversation_id": conversation_id,
                "messages": history
            }

        except Exception as e:
            logger.error(f"Erro ao recuperar histórico da conversa: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro interno no servidor")
