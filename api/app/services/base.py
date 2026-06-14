import uuid
from typing import ClassVar, Self

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.query_builder import QueryBuilder
from app.db.session import SessionDep
from app.errors import ConflictError, NotFoundError


class BaseService[ModelT, CreateSchemaT, UpdateSchemaT]:
    """
    BaseService[Model, CreateSchema, UpdateSchema]
    """

    model: ClassVar[type]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    def _builder(self) -> QueryBuilder[ModelT]:
        return QueryBuilder(self.model)

    async def get_by_id(self, id: uuid.UUID) -> ModelT:
        instance = await self.session.get(self.model, id)
        if instance is None:
            raise NotFoundError(self.model.__tablename__, id)
        return instance

    async def list(self, skip: int = 0, limit: int = 20) -> tuple[int, list[ModelT]]:
        builder = self._builder()
        total = await self.session.scalar(builder.count_stmt())
        result = await self.session.execute(builder.paginated(skip, limit))
        return total or 0, list(result.scalars().all())

    async def create(self, data: CreateSchemaT) -> ModelT:
        instance = self.model(id=generate_uuid(), **self._create_dict(data))
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, data: UpdateSchemaT) -> ModelT:
        instance = await self.get_by_id(id)
        for field, value in self._update_dict(data).items():
            setattr(instance, field, value)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID) -> None:
        instance = await self.get_by_id(id)
        await self.session.delete(instance)
        await self.session.commit()

    def _create_dict(self, data: CreateSchemaT) -> dict:
        return data.model_dump()  # type: ignore[union-attr]

    def _update_dict(self, data: UpdateSchemaT) -> dict:
        return data.model_dump(exclude_unset=True)  # type: ignore[union-attr]
