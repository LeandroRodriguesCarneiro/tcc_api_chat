from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import ConversationModel
from .repository import Repository

class ConversationRepository(Repository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, instance: ConversationModel) -> ConversationModel:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def add_many(self, instances: list[ConversationModel]) -> list[ConversationModel]:
        self.session.add_all(instances)
        self.session.commit()
        return instances

    def get_by_id(self, id: str) -> ConversationModel | None:
        result = self.session.execute(
            select(ConversationModel).where(ConversationModel.id == id)
        )
        return result.scalar_one_or_none()

    def get_all(self) -> list[ConversationModel]:
        result = self.session.execute(select(ConversationModel))
        return result.scalars().all()

    def delete(self, id: str) -> None:
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()

    def update(self, instance: ConversationModel) -> ConversationModel:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_user_id(
        self,
        user_id: int,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        order_desc: bool | None = None
    ):
        stmt = select(ConversationModel).where(ConversationModel.user_id == user_id)

        if order_by:
            column = getattr(ConversationModel, order_by, None)
            if column is not None:
                if order_desc or False:
                    stmt = stmt.order_by(column.desc())
                else:
                    stmt = stmt.order_by(column.asc())
        else:
            stmt = stmt.order_by(ConversationModel.updated_at.desc())

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.session.execute(stmt)
        return result.scalars().all()
