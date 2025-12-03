from sqlalchemy import Column, BigInteger, Text, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from .base_model import Base


class LanggraphCheckpointModel(Base):
    __tablename__ = "langgraph_checkpoints"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(Text, nullable=False, index=True)
    checkpoint = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
