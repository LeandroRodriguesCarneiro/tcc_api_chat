from pydantic import BaseModel
from typing import Optional

class ChatStartRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatSendRequest(BaseModel):
    conversation_id: str
    message: str