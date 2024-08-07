from abc import ABC, abstractmethod

from pydantic import BaseModel, PostgresDsn, MariaDBDsn, MySQLDsn, computed_field
from typing import ClassVar


class IBackend(ABC):
    @abstractmethod
    def get_dsn(self):
        raise NotImplemented


class BaseDSNModel(BaseModel, IBackend):
    __dialect__: ClassVar[str] = None

    driver: str = ""

    host: str | None = None
    port: int | None = None
    path: str | None = None
    username: str | None = None
    password: str | None = None

    @computed_field(return_type=str)
    @property
    def scheme(self):
        return f"{self.__dialect__}+{self.driver}"

    def _get_dsn(self, converter):
        if self.dsn:
            return str(self.dsn)
        filtered_dict = self.__dict__.copy()
        filtered_dict.pop("driver")
        filtered_dict.pop("dsn")
        filtered_dict["scheme"] = self.scheme
        dsn = converter.build(**filtered_dict)
        return str(dsn)

    def get_dsn(self):
        raise NotImplemented


class Postgresql(BaseDSNModel):
    __dialect__: ClassVar[str] = "postgresql"

    driver: str = "asyncpg"
    dsn: PostgresDsn | None = None

    @computed_field(return_type=str)
    @property
    def get_dsn(self):
        return self._get_dsn(PostgresDsn)


class MysqlDB(BaseDSNModel):
    __dialect__: ClassVar[str] = "mysql"
    dsn: MySQLDsn | None = None
    driver: str = "asyncmy"

    @computed_field(return_type=str)
    @property
    def get_dsn(self):
        return self._get_dsn(MySQLDsn)


class Sqlite(BaseModel, IBackend):
    __dialect__: ClassVar[str] = "sqlite"
    driver: str = "aiosqlite"
    path: str | None = None
    file: str | None = "sqlite.db"
