from typing import Any, ClassVar, Tuple
from sqlalchemy.orm import DeclarativeBase
from .mixins import CommonMixin
from fastapi_manager.utils.string import convert_to_snake_case


class BaseTable(CommonMixin, DeclarativeBase):
    repr_cols_num: ClassVar[int] = 3
    repr_cols: ClassVar[Tuple] = tuple()

    def __init_subclass__(cls, **kw: Any) -> None:
        super().__init_subclass__(**kw)
        cls.__table_args__ = {"schema": str(cls.__module__.split(".")[-2])}
        cls.__tablename__ = convert_to_snake_case(cls.__name__)

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
