from typing import Literal, TypeVar
from pydantic import BaseModel
from sqlalchemy import select, delete
from fastapi_manager.apps import apps
from fastapi_manager.db.models.base2 import BaseTable
import operator
from fastapi_manager.db import sessionmanager
from fastapi_manager.utils.async_class import AsyncObject

OPERATORS = Literal["eq", "gt", "ge", "lt", "le", "ne", "contains"]
_RETURN_TYPE = TypeVar("_RETURN_TYPE", bound=BaseModel)


class OnlyOneCRUDOperation(Exception):
    """
    You should use only one crud operation after from_table() method, for example FilterBuilde().from_table('table').select()
    """


class FilterBuilder(AsyncObject):

    model: type[BaseTable] = None
    table_name = None
    statement = None
    instance = None
    is_single = False

    # def __init__(self):
    #     self.model: type[BaseTable] = None
    #     self.table_name = None
    #     self.statement = None
    #     self.instance = None
    #     self.is_single = False

    async def __ainit__(self):
        self.instance = await self._perform_db_action()

    def __repr__(self):
        return self.instance

    def _get_model_column(self, col):
        try:
            return self.model.__dict__[col]
        except:
            raise Exception(f"{self.model} model does not have {col} column")

    def from_table(self, table_name: str):
        self.model = apps.get_model(table_name)
        self.table_name = table_name
        return self

    def select(self, cols: str = "*"):
        if self.statement is not None:
            raise OnlyOneCRUDOperation
        self.statement = select(self.model)

        if cols != "*":
            for column in cols.split(","):
                self.statement.add_columns(self._get_model_column(column))
        return self

    def delete(self):
        if self.statement is not None:
            raise OnlyOneCRUDOperation
        self.statement = delete(self.model)
        return self

    def filter(self, col_name: str, op: OPERATORS, col_value: str):
        self.statement = self.statement.filter(
            operator.__dict__[op](self._get_model_column(col_name), col_value)
        )
        return self

    def limit(self, limit):
        self.statement = self.statement.limit(limit)
        return self

    def returns[_RETURN_TYPE](self, pydantic_class: _RETURN_TYPE) -> _RETURN_TYPE:
        if self.instance is None:
            raise Exception("You need to execute statement")
        return pydantic_class.model_validate(self.instance)

    async def _perform_db_action(self):
        if self.statement is None:
            raise Exception(
                "You need make statement, for example FilterBuilde.from_table('table_1').select()"
            )
        async with sessionmanager.session() as session:
            result = await session.execute(self.statement)

            if self.is_single:
                return result.scalar_one_or_none()
            return result.scalars().all()
