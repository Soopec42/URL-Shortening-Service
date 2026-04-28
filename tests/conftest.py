import pytest
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.db.session as db_session_module
from app.db.session import Base, get_db
from app.main import create_app

TEST_DATABASE_URL = "postgresql+asyncpg://soop:gumanoid99@localhost:5433/my_short_url_test"

@pytest_asyncio.fixture()
async def engine():
    _engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await _engine.dispose()


@pytest_asyncio.fixture()
async def db_session(engine):
    factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )

    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def client(db_session):
    app = create_app()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()




