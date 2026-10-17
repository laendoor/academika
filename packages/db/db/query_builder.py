from sqlalchemy import Select, func, select
from sqlalchemy.sql._typing import _ColumnExpressionArgument


class QueryBuilder[ModelT]:
    def __init__(self, model: type[ModelT]) -> None:
        self._model = model
        self._stmt: Select = select(model)
        self._criteria: list[_ColumnExpressionArgument] = []

    def filter(self, *criteria: _ColumnExpressionArgument) -> "QueryBuilder[ModelT]":
        self._criteria.extend(criteria)
        return self

    def order_by(self, *columns: _ColumnExpressionArgument) -> "QueryBuilder[ModelT]":
        self._stmt = self._stmt.order_by(*columns)
        return self

    def build(self) -> Select:
        if self._criteria:
            return self._stmt.where(*self._criteria)
        return self._stmt

    def paginated(self, skip: int, limit: int) -> Select:
        return self.build().offset(skip).limit(limit)

    def count_stmt(self) -> Select:
        stmt = select(func.count()).select_from(self._model)
        if self._criteria:
            stmt = stmt.where(*self._criteria)
        return stmt
