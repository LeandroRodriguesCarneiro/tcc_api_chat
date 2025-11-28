from sqlalchemy import (
    Column, Integer, Text, DateTime, func, ForeignKey
)

from .base_model import Base

class ConversationModel(Base):
    __tablename__ = "conversations"
    id = Column(Text, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime)
    message_count = Column(Integer, default=0)