import os
from pathlib import Path
from unittest.mock import Mock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# fmt: off
os.environ["R2_ENDPOINT"] = "https://r2.test"
os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"
os.environ["R2_BUCKET"] = "test-bucket"
os.environ["R2_PUBLIC_URL"] = "https://cdn.test"

from app.auth.utils import create_token, hash_password
from app.core.config import settings
from app.models.brand import Brands
from app.models.category import Category
from app.models.image import Images
from app.models.product import Products
from app.models.users import User
from app.storage import r2
from database import Base

# fmt: on


class TestDatabaseSettings(BaseSettings):
    db_user: str
    db_password: str

    test_db_host: str
    test_db_port: int
    test_db_name: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    settings = TestDatabaseSettings()

    if settings.test_db_name != "cult111_test":
        raise RuntimeError(
            "Tests can only run against cult111_test"
        )

    if settings.test_db_host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(
            "Test database must be accessible through localhost"
        )

    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.test_db_host,
        port=settings.test_db_port,
        database=settings.test_db_name,
    )

    engine = create_async_engine(
        url,
        connect_args={"ssl": False},
    )

    schema_created = False

    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT current_database()")
            )
            actual_database = result.scalar_one()

            if actual_database != "cult111_test":
                raise RuntimeError(
                    "Connected to the wrong database!"
                )

            existing_tables = await connection.run_sync(
                lambda conn: inspect(conn).get_table_names()
            )

            if existing_tables:
                raise RuntimeError(
                    f"Test database is not empty: {existing_tables}"
                )

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        schema_created = True

        yield engine

    finally:
        try:
            if schema_created:
                async with engine.begin() as connection:
                    await connection.run_sync(Base.metadata.drop_all)
        finally:
            await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        try:
            async with AsyncSession(
                bind=connection,
                join_transaction_mode="create_savepoint",
                expire_on_commit=False,
            ) as session:
                yield session

        finally:
            await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    from app.dependency import get_db
    from main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def brand_factory(db_session):

    async def create_brand(name, is_visible: bool = True):
        brand = Brands(name=name, is_visible=is_visible)

        db_session.add(brand)
        await db_session.flush()

        return brand

    return create_brand


@pytest.fixture
def category_factory(db_session):

    async def create_category(name, is_visible: bool = True):

        category = Category(name=name, is_visible=is_visible)

        db_session.add(category)
        await db_session.flush()

        return category

    return create_category


@pytest.fixture
def product_factory(db_session):

    async def create_product(name, price, category_id, brand_id, is_visible: bool = True):

        product = Products(
            name=name,
            price=price,
            description="Test product",
            category_id=category_id,
            brand_id=brand_id,
            is_visible=is_visible
        )

        db_session.add(product)
        await db_session.flush()

        return product

    return create_product


@pytest.fixture
def user_factory(db_session):

    async def create_user(
        username,
        password="Test12345!",
        is_active=True,
        is_admin=False,
    ):
        user = User(
            username=username,
            nickname=username,
            password_hash=hash_password(password),
            is_active=is_active,
            is_admin=is_admin,
        )

        db_session.add(user)
        await db_session.flush()

        return user

    return create_user


@pytest_asyncio.fixture
async def regular_user(user_factory):
    return await user_factory(
        username="regular_user",
        is_active=True,
        is_admin=False,
    )


@pytest_asyncio.fixture
async def admin_user(user_factory):
    return await user_factory(
        username="admin_user",
        is_active=True,
        is_admin=True,
    )


@pytest_asyncio.fixture
async def inactive_user(user_factory):
    return await user_factory(
        username="inactive_user",
        is_active=False,
        is_admin=False,
    )


@pytest.fixture
def regular_user_headers(regular_user):
    token = create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user):
    token = create_token(
        user_id=admin_user.id,
        token_type="access",
        token_expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def inactive_user_headers(inactive_user):
    token = create_token(
        user_id=inactive_user.id,
        token_type="access",
        token_expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def r2_mock(monkeypatch):
    storage = Mock(
        spec=[
            "generate_presigned_url",
            "head_object",
            "copy_object",
            "delete_object",
        ]
    )

    storage.generate_presigned_url.return_value = (
        "https://storage.test/upload"
    )

    storage.head_object.return_value = {
        "ContentType": "image/png",
        "ContentLength": 100,
    }

    monkeypatch.setattr(r2, "s3", storage)

    return storage
