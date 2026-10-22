import pytest
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import inspect
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from database import Base
from app.models.brand import Brands
from app.models.category import Category
from app.models.product import Products
from app.models.image import Images


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


@pytest.fixture(scope="session")
def test_engine():
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
        drivername="postgresql+psycopg2",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.test_db_host,
        port=settings.test_db_port,
        database=settings.test_db_name,
    )

    engine = create_engine(
        url,
        connect_args={"sslmode": "disable"},
    )

    schema_created = False

    try:
        # Проверяем настоящее имя подключённой базы
        with engine.connect() as connection:
            actual_database = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

            if actual_database != "cult111_test":
                raise RuntimeError(
                    "Connected to the wrong database!"
                )

        # Проверяем, что тестовая база пустая
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if existing_tables:
            raise RuntimeError(
                f"Test database is not empty: {existing_tables}"
            )

        # Создаём таблицы
        Base.metadata.create_all(bind=engine)
        schema_created = True

        yield engine

    finally:
        if schema_created:
            Base.metadata.drop_all(bind=engine)

        engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        with Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    from main import app
    from app.dependency import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def brand_factory(db_session):

    def create_brand(name, is_visible: bool = True):

        brand = Brands(name=name, is_visible=is_visible)

        db_session.add(brand)
        db_session.flush()

        return brand

    return create_brand


@pytest.fixture
def category_factory(db_session):

    def create_category(name, is_visible: bool = True):

        category = Category(name=name, is_visible=is_visible)

        db_session.add(category)
        db_session.flush()

        return category

    return create_category


@pytest.fixture
def product_factory(db_session):

    def create_product(name, price, category_id, brand_id, is_visible: bool = True):

        product = Products(
            name=name,
            price=price,
            description="Test product",
            category_id=category_id,
            brand_id=brand_id,
            is_visible=is_visible
        )

        db_session.add(product)
        db_session.flush()

        return product

    return create_product
