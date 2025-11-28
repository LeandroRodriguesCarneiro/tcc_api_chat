from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..models import MessageModel

class MessageDTO(BaseModel):
    id: Optional[str] = Field(default=None)
    conversation_id: str
    role: str
    content: str
    timestamp: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

    def to_model(self):
        data = self.model_dump(exclude_unset=True)
        from ..models import MessageModel
        return MessageModel(**data)