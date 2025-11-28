from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import MessageModel
from .repository import Repository

class MessageRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, instance: MessageModel) -> MessageModel:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def add_many(self, instances: list[MessageModel]) -> list[MessageModel]:
        self.session.add_all(instances)
        self.session.commit()
        return instances

    def get_by_id(self, id: str) -> MessageModel | None:
        result = self.session.execute(
            select(MessageModel).where(MessageModel.id == id)
        )
        return result.scalar_one_or_none()

    def get_by_conversation_id(
        self,
        conversation_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_desc: bool | None = None,
        order_by: str | None = None,
    ) -> list[MessageModel]:
        if order_by is not None:
            order_desc = order_by.lower() == "desc"

        if order_desc is None:
            order_desc = False

        stmt = select(MessageModel).where(MessageModel.conversation_id == conversation_id)

        if order_desc:
            stmt = stmt.order_by(MessageModel.timestamp.desc())
        else:
            stmt = stmt.order_by(MessageModel.timestamp.asc())

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.session.execute(stmt)
        return result.scalars().all()


    def get_all(self) -> list[MessageModel]:
        result = self.session.execute(select(MessageModel))
        return result.scalars().all()

    def delete(self, id: str) -> None:
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()

    def update(self, instance: MessageModel) -> MessageModel:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
