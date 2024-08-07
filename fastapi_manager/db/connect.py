import contextlib
from typing import Any, AsyncGenerator, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncConnection,
)

from .utils import validate_database, DatabaseManagerError
from fastapi_manager.conf import settings
from fastapi_manager.utils.lazy import LazyObject


class DatabaseSessionManager:
    def __init__(self, engine_kwargs: dict[str, Any] = {}):
        self._database_url = validate_database(settings)
        self._engine = create_async_engine(self._database_url, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            raise DatabaseManagerError("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseManagerError("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except DatabaseManagerError:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise DatabaseManagerError("DatabaseSessionManager is not initialized")

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except DatabaseManagerError:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = LazyObject(lambda: DatabaseSessionManager({"echo": settings.DEBUG}))


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session
