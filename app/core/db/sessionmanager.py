import contextlib
from typing import Any, AsyncGenerator, AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import base


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kw: dict[str, Any] | None = None):
        engine_kw = engine_kw or {}
        defaults = {
            "future": True,
            "pool_size": 10,
            "max_overflow": 5,
            "pool_timeout": 30,
            "pool_recycle": 1800
        }
        self._engine = create_async_engine(
            host,  # type: ignore
            **{**defaults, **engine_kw}
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
            future=True
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.close()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._sessionmaker() as session:
            try:
                yield session
            except SQLAlchemyError:
                await session.rollback()
            finally:
                await session.close()


sessionmanager = DatabaseSessionManager(base.DB_URL or "")


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Async session generator for FastAPI dependency injection.

    Usage in a route:
        async def endpoint(db: AsyncSession = Depends(get_session)):
            ...
    Ensures automatic commit/rollback and safe connection cleanup
    through DatabaseSessionManager.
    """
    async with sessionmanager.session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
