from sqlalchemy import (
    Column, Integer, Text, DateTime, func, ForeignKey
)

from .base_model import Base

class MessageModel(Base):
    __tablename__ = "messages"
    id = Column(Text, primary_key=True)
    conversation_id = Column(Text, ForeignKey("conversations.id"))
    role = Column(Text)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())