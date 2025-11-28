from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from .base_model import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    token_version = Column(Integer, default=1)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    def is_locked(self) -> bool:
        """Retorna True se o usuário estiver bloqueado (por 1h após 5 falhas)."""
        return (
            self.locked_until is not None
            and self.locked_until > datetime.now(timezone.utc)
        )

    def __repr__(self):
        return (
            f"<User(id={self.id}, email={self.email}, full_name={self.full_name}, "
            f"is_active={self.is_active}, login_attempts={self.login_attempts}, "
            f"locked_until={self.locked_until}, created_at={self.created_at}, "
            f"updated_at={self.updated_at})>"
        )