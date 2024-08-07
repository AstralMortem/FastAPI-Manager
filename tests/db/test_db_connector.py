from functools import cached_property

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    AsyncConnection,
)

from fastapi_manager.db.connect import DatabaseSessionManager
from fastapi_manager.conf import settings
from fastapi_manager.utils.lazy import LazyObject


@pytest.fixture(autouse=True)
def set_database_url():
    settings.DATABASES = {
        "default": {
            "ENGINE": "fastapi_manager.db.backends.Postgresql",
            "OPTIONS": {
                "host": "localhost",
                "port": 5432,
                "username": "test_user",
                "password": "test_password",
                "path": "test_db",
            },
        }
    }


class TestSessionManager:
    @cached_property
    def sessionmanager(self):
        return DatabaseSessionManager()

    @pytest.mark.dependency()
    def test_sessionmanager_init(self):
        assert (
            self.sessionmanager._database_url
            == "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
        )

        assert isinstance(self.sessionmanager._engine, AsyncEngine)
        assert isinstance(self.sessionmanager._sessionmaker, async_sessionmaker)

    @pytest.mark.asyncio
    async def test_connection(self):
        async with self.sessionmanager.connect() as connection:
            assert isinstance(connection, AsyncConnection)

    @pytest.mark.asyncio
    async def test_session(self):
        async with self.sessionmanager.session() as session:
            assert isinstance(session, AsyncSession)


class TestLazySessionManager:

    @cached_property
    def sessionmanager(self):
        return LazyObject(lambda: DatabaseSessionManager())

    def test_sessionmanager_init(self):
        assert self.sessionmanager._wrapped is None
        assert (
            self.sessionmanager._database_url
            == "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
        )
        assert isinstance(self.sessionmanager._wrapped, DatabaseSessionManager)

    @pytest.mark.asyncio
    async def test_connection(self):
        async with self.sessionmanager.connect() as connection:
            assert isinstance(connection, AsyncConnection)

    @pytest.mark.asyncio
    async def test_session(self):
        async with self.sessionmanager.session() as session:
            assert isinstance(session, AsyncSession)


#
#
#
#

#
#

#
#
# @pytest.mark.asyncio
# async def test_lazy_connection(get_sessionmanager):
#     async with get_sessionmanager.connect() as connection:
#         assert isinstance(connection, AsyncConnection)
#
#
# @pytest.mark.asyncio
# async def test_lazy_session(get_sessionmanager):
#     async with get_sessionmanager.session() as session:
#         assert isinstance(session, AsyncSession)
