from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..models import ConversationModel

class ConversationDTO(BaseModel):
    id: Optional[str] = Field(default=None)
    user_id: int
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0

    model_config = {
        "from_attributes": True
    }

    def to_model(self):
        data = self.model_dump(exclude_unset=True)
        return ConversationModel(**data)