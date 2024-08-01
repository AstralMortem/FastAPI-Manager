from typing import ClassVar, Tuple
from sqlmodel import SQLModel
from .mixins import DefaultMixin


class BaseTable(SQLModel, DefaultMixin, table=True):
    repr_cols_num: ClassVar[int] = 3
    repr_cols: ClassVar[Tuple] = tuple()

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
