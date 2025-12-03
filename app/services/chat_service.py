import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models import (
    ConversationModel, 
    MessageModel,
)
from ..dtos import (
    ConversationDTO, 
    MessageDTO,
)

from ..repositories import(
    ConversationRepository,
    MessageRepository,
    UserRepository
)

from ..database import Database
from ..loggin import logger

database = Database()

class ChatService:
    def __init__(self, db: Session, llm_service):
        self.db = db
        self.llm_service = llm_service
        self._init_repositories()

    def _init_repositories(self) -> None:
        self.conversation_repo = ConversationRepository(self.db)
        self.message_repo = MessageRepository(self.db)
        self.user_repo = UserRepository(self.db)

    def create_conversation(self, access_token: str) -> ConversationModel:
        """Cria uma nova conversa para o usuário"""
        try:
            user_id = self._extract_user_id_from_token(access_token)
            user = self.user_repo.get_by_id(user_id)
            
            if not user:
                raise ValueError("Usuário não encontrado")
            
            conversation_dto = ConversationDTO(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title="",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            conversation_model = self.conversation_repo.add(conversation_dto.to_model())
            logger.info(f"Nova conversa criada: {conversation_model.id} para user: {user_id}")
            
            return conversation_model
            
        except Exception as e:
            logger.error(f"Erro ao criar conversa: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[ConversationModel]:
        """Recupera uma conversa pelo ID"""
        try:
            conversation = self.conversation_repo.get_by_id(conversation_id)
            return conversation
        except Exception as e:
            logger.error(f"Erro ao buscar conversa {conversation_id}: {str(e)}")
            return None

    def get_user_conversations(self, access_token: str, limit: int = 10) -> List[ConversationModel]:
        """Lista conversas do usuário ordenadas por data mais recente"""
        try:
            user_id = self._extract_user_id_from_token(access_token)
            conversations = self.conversation_repo.get_by_user_id(user_id, limit=limit, order_by="updated_at")
            return conversations
        except Exception as e:
            logger.error(f"Erro ao listar conversas do usuário: {str(e)}")
            return []

    def add_message(self, conversation_id: str, role: str, content: str) -> MessageModel:
        """Adiciona uma mensagem à conversa"""
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversa {conversation_id} não encontrada")
            
            is_first_user_message = (
                role == "user" and 
                (conversation.title is None or conversation.title == "")
            )

            message_dto = MessageDTO(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=datetime.now(timezone.utc)
            )
            
            message_model = self.message_repo.add(message_dto.to_model())
            
            conversation.updated_at = datetime.now(timezone.utc)

            if is_first_user_message:
                conversation.title = self.llm_service.generate_title(content)
            
            conversation.message_count += 1
            self.conversation_repo.update(conversation)

            logger.info(f"Mensagem adicionada à conversa {conversation_id}: {role}")
            return message_model
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {str(e)}")
            raise

    def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[MessageModel]:
        """Recupera mensagens de uma conversa (mais recentes primeiro)"""
        try:
            messages = self.message_repo.get_by_conversation_id(
                conversation_id, 
                limit=limit, 
                offset=offset,
                order_by="timestamp"
            )
            return messages
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens da conversa {conversation_id}: {str(e)}")
            return []

    def generate_response(self, conversation_id: str, user_message: str) -> str:
        """Gera resposta usando o serviço LLM com memória persistente por thread_id"""

        try:
            thread_id = conversation_id

            response = self.llm_service.query(
                user_message=user_message,
                thread_id=thread_id
            )

            logger.info(f"Resposta gerada para conversa {conversation_id}")
            return response

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, não consegui processar sua mensagem no momento. Tente novamente."

    
    def _extract_user_id_from_token(self, access_token: str) -> str:
        """Extrai user_id do token JWT (implemente conforme sua SecurityService)"""
        from ..services import SecurityService
        security = SecurityService()
        payload = security.validate_access_token(access_token)
        return payload.get("id")

    def _build_conversation_context(self, messages: List[MessageModel]) -> List[Dict[str, str]]:
        """Constrói contexto formatado para o LLM"""
        context = []
        for msg in reversed(messages):
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        return context

    def _generate_conversation_title(self, first_message: str, max_length: int = 50) -> str:
        """Gera título da conversa baseado na primeira mensagem"""
        title = first_message[:max_length].strip()
        if len(first_message) > max_length:
            title += "..."
        return title or "Nova conversa"