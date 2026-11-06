from collections.abc import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from unittest import mock

import app.services.file as file_service
from app.api.deps import get_db
from app.core.config import get_settings, get_settings_s3
from app.core.database import Base
from app.main import app

load_dotenv('./../.env.test', override=True)

file_service.CLIENT = mock.Mock()
file_service.PUBLIC_CLIENT = mock.Mock()
file_service.PUBLIC_CLIENT.presigned_get_object.return_value = (
    "http://localhost:9000/test_bucket/{}.jpg?signature=test"
)

settings = get_settings()
s3_settings = get_settings_s3()

settings.database_url = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(settings.database_url, future=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
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
