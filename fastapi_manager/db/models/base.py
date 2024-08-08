from typing import Any, ClassVar, Tuple
from sqlalchemy.orm import DeclarativeBase
from .mixins import CommonMixin
from fastapi_manager.utils.string import convert_to_snake_case
from fastapi_manager.apps import apps


class BaseTable(DeclarativeBase, CommonMixin):
    repr_cols_num: ClassVar[int] = 3
    repr_cols: ClassVar[Tuple] = tuple()

    def __init_subclass__(cls, **kwargs):
        cls.__tablename__ = convert_to_snake_case(cls.__name__)

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
