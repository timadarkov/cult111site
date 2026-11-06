import re
import pytest

from fastapi.routing import APIRoute
from sqlalchemy import select

from main import app
from app.models.brand import Brands
from app.models.category import Category
from app.models.product import Products
from app.models.info import Info
from app.models.users import User


admin_routes = [
    route
    for route in app.routes
    if isinstance(route, APIRoute)
    and route.path.startswith("/api/v1/admin/")
]

endpoints = [
    (method, route.path)
    for route in admin_routes
    for method in route.methods
]

assert endpoints, "No admin endpoints discovered"


@pytest.mark.parametrize("method, path", endpoints)
def test_admin_requires_auth(client, method, path):
    url = re.sub(r"\{[^{}]+\}", "123", path)

    response = client.request(method, url)

    assert response.status_code == 401


def test_admin_create_brand(client, admin_headers, db_session):
    response = client.post(
        "/api/v1/admin/brands",
        headers=admin_headers,
        json={
            "name": "Nike",
            "is_visible": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Nike"
    assert "id" in data

    brand = db_session.scalar(
        select(Brands).where(Brands.id == data["id"])
    )

    assert brand is not None
    assert brand.name == "Nike"
    assert brand.is_visible is True


def test_regular_user_cannot_create_brand(
    client, regular_user_headers, db_session
):
    response = client.post(
        "/api/v1/admin/brands",
        headers=regular_user_headers,
        json={
            "name": "Adidas",
            "is_visible": True,
        },
    )

    assert response.status_code == 403
    brand = db_session.scalar(
        select(Brands).where(Brands.name == "Adidas")
    )

    assert brand is None


def test_admin_create_duplicate_brand(
    client, admin_headers, brand_factory
):
    brand_factory(name="Nike")

    response = client.post(
        "/api/v1/admin/brands",
        headers=admin_headers,
        json={"name": "Nike"},
    )

    assert response.status_code == 409


def test_admin_edit_duplicate_brand(
    client, admin_headers, brand_factory, db_session
):
    brand_factory(name="Nike")
    adidas = brand_factory(name="Adidas")

    db_session.commit()

    response = client.patch(
        f"/api/v1/admin/brands/{adidas.id}",
        headers=admin_headers,
        json={"name": "Nike"},
    )

    assert response.status_code == 409

    db_session.expire_all()
    brand = db_session.get(Brands, adidas.id)

    assert brand is not None
    assert brand.name == "Adidas"


def test_admin_edit_brand(
    client, admin_headers, brand_factory, db_session
):
    brand = brand_factory(name="Nike")

    response = client.patch(
        f"/api/v1/admin/brands/{brand.id}",
        headers=admin_headers,
        json={"name": "Adidas"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Adidas"

    db_session.refresh(brand)

    assert brand.name == "Adidas"


def test_admin_update_brand_visibility(
    client, admin_headers, brand_factory, db_session
):
    brand = brand_factory(name="Nike", is_visible=True)

    response = client.patch(
        f"/api/v1/admin/brands/{brand.id}/visibility",
        headers=admin_headers,
        json={"is_visible": False},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["is_visible"] is False

    db_session.refresh(brand)

    assert brand.is_visible is False


def test_hidden_brand_visibility(
    client, admin_headers, brand_factory
):
    brand = brand_factory(
        name="Nike",
        is_visible=False,
    )

    public_response = client.get("/api/v1/brands")
    admin_response = client.get(
        "/api/v1/admin/brands",
        headers=admin_headers,
    )

    assert public_response.status_code == 200
    assert admin_response.status_code == 200

    public_ids = [
        item["id"] for item in public_response.json()
    ]

    admin_ids = [
        item["id"] for item in admin_response.json()
    ]

    assert brand.id not in public_ids
    assert brand.id in admin_ids


def test_admin_create_category(client, admin_headers, db_session):
    response = client.post(
        "/api/v1/admin/categories",
        headers=admin_headers,
        json={
            "name": "Electronics",
            "is_visible": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Electronics"
    assert "id" in data

    category = db_session.get(Category, data["id"])

    assert category is not None
    assert category.name == "Electronics"
    assert category.is_visible is True


def test_admin_create_hidden_category(
    client, admin_headers, db_session
):
    response = client.post(
        "/api/v1/admin/categories",
        headers=admin_headers,
        json={
            "name": "Hidden Electronics",
            "is_visible": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    category = db_session.get(Category, data["id"])

    assert category is not None
    assert category.is_visible is False


def test_admin_create_duplicate_category(
    client, admin_headers, category_factory
):
    category_factory(name="Electronics")

    response = client.post(
        "/api/v1/admin/categories",
        headers=admin_headers,
        json={"name": "Electronics"},
    )

    assert response.status_code == 409


def test_admin_edit_duplicate_category(
    client, admin_headers, category_factory, db_session
):
    category_factory(name="Electronics")
    phones = category_factory(name="Phones")

    db_session.commit()

    response = client.patch(
        f"/api/v1/admin/categories/{phones.id}",
        headers=admin_headers,
        json={"name": "Electronics"},
    )

    assert response.status_code == 409

    db_session.expire_all()

    category = db_session.get(Category, phones.id)

    assert category is not None
    assert category.name == "Phones"


def test_admin_edit_category(
    client, admin_headers, category_factory, db_session
):
    category = category_factory(name="Electronics")

    response = client.patch(
        f"/api/v1/admin/categories/{category.id}",
        headers=admin_headers,
        json={"name": "Smartphones"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Smartphones"

    db_session.refresh(category)

    assert category.name == "Smartphones"


def test_admin_update_category_visibility(
    client, admin_headers, category_factory, db_session
):
    category = category_factory(
        name="Electronics",
        is_visible=True,
    )

    response = client.patch(
        f"/api/v1/admin/categories/{category.id}/visibility",
        headers=admin_headers,
        json={"is_visible": False},
    )

    assert response.status_code == 200
    assert response.json()["is_visible"] is False

    db_session.refresh(category)

    assert category.is_visible is False


def test_hidden_category_visibility(
    client, admin_headers, category_factory
):
    category = category_factory(
        name="Electronics",
        is_visible=False,
    )

    public_response = client.get("/api/v1/categories")

    admin_response = client.get(
        "/api/v1/admin/categories",
        headers=admin_headers,
    )

    assert public_response.status_code == 200
    assert admin_response.status_code == 200

    public_ids = [
        item["id"] for item in public_response.json()
    ]

    admin_ids = [
        item["id"] for item in admin_response.json()
    ]

    assert category.id not in public_ids
    assert category.id in admin_ids


def test_admin_delete_category(
    client, admin_headers, category_factory, db_session
):
    category = category_factory(name="Electronics")
    category_id = category.id

    response = client.delete(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()

    assert db_session.get(Category, category_id) is None


def test_admin_cannot_delete_category_with_products(
    client,
    admin_headers,
    category_factory,
    brand_factory,
    product_factory,
    db_session,
):
    category = category_factory(name="Electronics")
    brand = brand_factory(name="Nike")

    product = product_factory(
        name="Phone",
        price=1000,
        category_id=category.id,
        brand_id=brand.id,
    )

    category_id = category.id
    product_id = product.id

    db_session.commit()

    response = client.delete(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

    db_session.expire_all()

    assert db_session.get(Category, category_id) is not None
    assert db_session.get(Products, product_id) is not None


def test_admin_delete_brand(
    client, admin_headers, brand_factory, db_session
):
    brand = brand_factory(name="Nike")
    brand_id = brand.id

    response = client.delete(
        f"/api/v1/admin/brands/{brand_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()
    assert db_session.get(Brands, brand_id) is None


def test_admin_cannot_delete_brand_with_products(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Electronics")

    product = product_factory(
        name="Phone",
        price=1000,
        brand_id=brand.id,
        category_id=category.id,
    )

    brand_id = brand.id
    product_id = product.id

    db_session.commit()

    response = client.delete(
        f"/api/v1/admin/brands/{brand_id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

    db_session.expire_all()

    assert db_session.get(Brands, brand_id) is not None
    assert db_session.get(Products, product_id) is not None


def test_admin_create_product(
    client, admin_headers, brand_factory, category_factory, db_session
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    response = client.post(
        "/api/v1/admin/products",
        headers=admin_headers,
        json={
            "name": "Air Max",
            "price": 150,
            "description": "Running shoes",
            "brand_id": brand.id,
            "category_id": category.id,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Air Max"
    assert data["price"] == 150

    product = db_session.get(Products, data["id"])
    assert product is not None
    assert product.name == "Air Max"


def test_admin_partial_update_product(
    client, admin_headers, product_factory,
    brand_factory, category_factory, db_session
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    product = product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    response = client.patch(
        f"/api/v1/admin/products/{product.id}",
        headers=admin_headers,
        json={"price": 200},
    )

    assert response.status_code == 200

    db_session.refresh(product)

    assert float(product.price) == 200
    assert product.name == "Air Max"
    assert product.description == "Test product"


@pytest.mark.parametrize("price", [0, -1, -100])
def test_admin_cannot_create_product_with_invalid_price(
    client, admin_headers, brand_factory, category_factory, price
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    response = client.post(
        "/api/v1/admin/products",
        headers=admin_headers,
        json={
            "name": "Air Max",
            "price": price,
            "description": "Running shoes",
            "brand_id": brand.id,
            "category_id": category.id,
        },
    )

    assert response.status_code == 422


def test_hidden_product_visibility(
    client, admin_headers, product_factory,
    brand_factory, category_factory
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    product = product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
        is_visible=False,
    )

    public_response = client.get("/api/v1/products")

    admin_response = client.get(
        "/api/v1/admin/products",
        headers=admin_headers,
    )

    assert public_response.status_code == 200
    assert admin_response.status_code == 200

    public_ids = [p["id"] for p in public_response.json()]
    admin_ids = [p["id"] for p in admin_response.json()]

    assert product.id not in public_ids
    assert product.id in admin_ids


@pytest.mark.parametrize("price", [0, -1, -100])
def test_admin_cannot_update_product_with_invalid_price(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
    price,
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    product = product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    response = client.patch(
        f"/api/v1/admin/products/{product.id}",
        headers=admin_headers,
        json={"price": price},
    )

    assert response.status_code == 422

    db_session.refresh(product)
    assert float(product.price) == 150


def test_admin_soft_delete_product(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
):
    brand = brand_factory(name="Nike")
    category = category_factory(name="Shoes")

    product = product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    product_id = product.id

    response = client.delete(
        f"/api/v1/admin/products/{product_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()

    saved_product = db_session.get(Products, product_id)

    assert saved_product is not None
    assert saved_product.is_visible is False

    public_response = client.get("/api/v1/products")
    admin_response = client.get(
        "/api/v1/admin/products",
        headers=admin_headers,
    )

    assert public_response.status_code == 200
    assert admin_response.status_code == 200

    public_ids = [p["id"] for p in public_response.json()]
    admin_ids = [p["id"] for p in admin_response.json()]

    assert product_id not in public_ids
    assert product_id in admin_ids


def test_admin_create_info(client, admin_headers, db_session):
    response = client.post(
        "/api/v1/admin/info",
        headers=admin_headers,
        json={
            "slug": "about",
            "info": "About our shop",
            "owners": "Timofei",
            "contacts": "support@example.com",
        },
    )

    assert response.status_code == 201

    record = db_session.get(Info, "about")

    assert record is not None
    assert record.info == "About our shop"

    public_response = client.get("/api/v1/info")

    assert public_response.status_code == 200
    assert any(
        item["slug"] == "about"
        for item in public_response.json()
    )


def test_admin_update_info(client, admin_headers, db_session):
    record = Info(
        slug="about",
        info="Old information",
        owners="Timofei",
        contacts="old@example.com",
    )
    db_session.add(record)
    db_session.flush()

    response = client.patch(
        "/api/v1/admin/info/about",
        headers=admin_headers,
        json={"info": "New information"},
    )

    assert response.status_code == 200

    db_session.refresh(record)

    assert record.info == "New information"
    assert record.owners == "Timofei"
    assert record.contacts == "old@example.com"


def test_hidden_info_not_public(client, admin_headers, db_session):
    record = Info(
        slug="secret",
        info="Private information",
        owners="Timofei",
        contacts="private@example.com",
        is_visible=False,
    )
    db_session.add(record)
    db_session.flush()

    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert all(
        item["slug"] != "secret"
        for item in response.json()
    )

    assert db_session.get(Info, "secret") is not None


def test_admin_create_user(client, admin_headers, db_session):
    response = client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={
            "username": "newuser123",
            "password": "Test12345!",
            "nickname": "New User",
            "email": "newuser@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "newuser123"
    assert data["nickname"] == "New User"

    assert "password" not in data
    assert "password_hash" not in data

    user = db_session.get(User, data["id"])

    assert user is not None
    assert user.password_hash != "Test12345!"
    assert user.is_active is True


def test_regular_user_cannot_create_user(
    client, regular_user_headers, db_session
):
    response = client.post(
        "/api/v1/admin/users",
        headers=regular_user_headers,
        json={
            "username": "blocked123",
            "password": "Test12345!",
            "nickname": "Blocked",
        },
    )

    assert response.status_code == 403

    user = db_session.query(User).filter(
        User.username == "blocked123"
    ).first()

    assert user is None
