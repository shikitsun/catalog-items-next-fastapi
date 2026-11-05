from collections.abc import AsyncGenerator

import pytest_asyncio
from alembic.config import Config
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command

load_dotenv('./../.env.test', override=False)

from app.api.deps import get_db
from app.core.config import get_settings, get_settings_s3
from app.main import app

settings = get_settings()
s3_settings = get_settings_s3()
test_engine = create_async_engine(settings.database_url, future=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with test_engine.begin() as conn:
        def upgrade(sync_conn):
            cfg = Config("./alembic.ini")
            cfg.attributes["connection"] = sync_conn
            command.upgrade(cfg, 'head')
        await conn.run_sync(upgrade)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        async with TestSessionLocal(bind=conn) as session:
            yield session
        await trans.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
