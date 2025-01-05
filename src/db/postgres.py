import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as alchemy_async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from src import config

log = logging.getLogger(__name__)


# Инициализация движка
_engine: AsyncEngine = create_async_engine(
    config.DB_URL,
    echo=config.IS_DEBUG,
)
_async_session_maker = alchemy_async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_maker() as session:
        yield session


async def init_db() -> None:
    try:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info('Database initialized successfully.')
    except SQLAlchemyError as e:
        log.error(f'An error occurred while initializing the database: {e}')
    except Exception as e:
        log.error(f'An unexpected error occurred: {e}')


class Base(DeclarativeBase):
    pass
