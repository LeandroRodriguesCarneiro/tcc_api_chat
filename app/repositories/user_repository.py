from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone, timedelta

from app.models.user_model import UserModel

from .repository import Repository

class UserRepository(Repository):
    def __init__(self, session: Session):
        super().__init__(session)

    MAX_LOGIN_ATTEMPTS = 5
    LOCK_DURATION = timedelta(hours=1)

    def add(self, user: UserModel):
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: int):
        return self.session.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str):
        return self.session.query(UserModel).filter(UserModel.email == email).first()

    def get_all(self):
        return self.session.query(UserModel).options(joinedload(UserModel.process)).all()

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
        return user

    def update(self, user: UserModel):
        self.session.merge(user)
        self.session.commit()
        return user