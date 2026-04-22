from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_setting

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

class Base(DeclarativeBase):
    """Base"""


def build_engine(database_url: str | None = None):
    url = database_url or get_setting().database_url
    return create_async_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

def buil_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind = engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None

def get_engine():
    global _engine
    if _engine == None:
        _engine = build_engine()
    return _engine

def get_session_factory():
    global _session_factory
    if _session_factory == None:
        _session_factory = buil_session_factory(get_engine())
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise



