import re

import pytest
from fastapi.routing import APIRoute
from sqlalchemy import select

from app.models.brand import Brands
from app.models.category import Category
from app.models.info import Info
from app.models.product import Products
from app.models.users import User
from main import app

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
async def test_admin_requires_auth(client, method, path):
    url = re.sub(r"\{[^{}]+\}", "123", path)

    response = await client.request(method, url)

    assert response.status_code == 401


async def test_admin_create_brand(client, admin_headers, db_session):
    response = await client.post(
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

    brand = await db_session.scalar(
        select(Brands).where(Brands.id == data["id"])
    )

    assert brand is not None
    assert brand.name == "Nike"
    assert brand.is_visible is True


async def test_regular_user_cannot_create_brand(
    client, regular_user_headers, db_session
):
    response = await client.post(
        "/api/v1/admin/brands",
        headers=regular_user_headers,
        json={
            "name": "Adidas",
            "is_visible": True,
        },
    )

    assert response.status_code == 403
    brand = await db_session.scalar(
        select(Brands).where(Brands.name == "Adidas")
    )

    assert brand is None


async def test_admin_create_duplicate_brand(
    client, admin_headers, brand_factory
):
    await brand_factory(name="Nike")

    response = await client.post(
        "/api/v1/admin/brands",
        headers=admin_headers,
        json={"name": "Nike"},
    )

    assert response.status_code == 409


async def test_admin_edit_duplicate_brand(
    client, admin_headers, brand_factory, db_session
):
    await brand_factory(name="Nike")
    adidas = await brand_factory(name="Adidas")

    adidas_id = adidas.id

    await db_session.commit()

    response = await client.patch(
        f"/api/v1/admin/brands/{adidas_id}",
        headers=admin_headers,
        json={"name": "Nike"},
    )

    assert response.status_code == 409

    db_session.expire_all()
    brand = await db_session.get(Brands, adidas_id)

    assert brand is not None
    assert brand.name == "Adidas"


async def test_admin_edit_brand(
    client, admin_headers, brand_factory, db_session
):
    brand = await brand_factory(name="Nike")

    response = await client.patch(
        f"/api/v1/admin/brands/{brand.id}",
        headers=admin_headers,
        json={"name": "Adidas"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Adidas"

    await db_session.refresh(brand)

    assert brand.name == "Adidas"


async def test_admin_update_brand_visibility(
    client, admin_headers, brand_factory, db_session
):
    brand = await brand_factory(name="Nike", is_visible=True)

    response = await client.patch(
        f"/api/v1/admin/brands/{brand.id}/visibility",
        headers=admin_headers,
        json={"is_visible": False},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["is_visible"] is False

    await db_session.refresh(brand)

    assert brand.is_visible is False


async def test_hidden_brand_visibility(
    client, admin_headers, brand_factory
):
    brand = await brand_factory(
        name="Nike",
        is_visible=False,
    )

    public_response = await client.get("/api/v1/brands")
    admin_response = await client.get(
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


async def test_admin_create_category(client, admin_headers, db_session):
    response = await client.post(
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

    category = await db_session.get(Category, data["id"])

    assert category is not None
    assert category.name == "Electronics"
    assert category.is_visible is True


async def test_admin_create_hidden_category(
    client, admin_headers, db_session
):
    response = await client.post(
        "/api/v1/admin/categories",
        headers=admin_headers,
        json={
            "name": "Hidden Electronics",
            "is_visible": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    category = await db_session.get(Category, data["id"])

    assert category is not None
    assert category.is_visible is False


async def test_admin_create_duplicate_category(
    client, admin_headers, category_factory
):
    await category_factory(name="Electronics")

    response = await client.post(
        "/api/v1/admin/categories",
        headers=admin_headers,
        json={"name": "Electronics"},
    )

    assert response.status_code == 409


async def test_admin_edit_duplicate_category(
    client, admin_headers, category_factory, db_session
):
    await category_factory(name="Electronics")
    phones = await category_factory(name="Phones")
    phones_id = phones.id
    await db_session.commit()

    response = await client.patch(
        f"/api/v1/admin/categories/{phones_id}",
        headers=admin_headers,
        json={"name": "Electronics"},
    )

    assert response.status_code == 409

    db_session.expire_all()

    category = await db_session.get(Category, phones_id)

    assert category is not None
    assert category.name == "Phones"


async def test_admin_edit_category(
    client, admin_headers, category_factory, db_session
):
    category = await category_factory(name="Electronics")

    response = await client.patch(
        f"/api/v1/admin/categories/{category.id}",
        headers=admin_headers,
        json={"name": "Smartphones"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Smartphones"

    await db_session.refresh(category)

    assert category.name == "Smartphones"


async def test_admin_update_category_visibility(
    client, admin_headers, category_factory, db_session
):
    category = await category_factory(
        name="Electronics",
        is_visible=True,
    )

    response = await client.patch(
        f"/api/v1/admin/categories/{category.id}/visibility",
        headers=admin_headers,
        json={"is_visible": False},
    )

    assert response.status_code == 200
    assert response.json()["is_visible"] is False

    await db_session.refresh(category)

    assert category.is_visible is False


async def test_hidden_category_visibility(
    client, admin_headers, category_factory
):
    category = await category_factory(
        name="Electronics",
        is_visible=False,
    )

    public_response = await client.get("/api/v1/categories")

    admin_response = await client.get(
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


async def test_admin_delete_category(
    client, admin_headers, category_factory, db_session
):
    category = await category_factory(name="Electronics")
    category_id = category.id

    response = await client.delete(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()

    assert await db_session.get(Category, category_id) is None


async def test_admin_cannot_delete_category_with_products(
    client,
    admin_headers,
    category_factory,
    brand_factory,
    product_factory,
    db_session,
):
    category = await category_factory(name="Electronics")
    brand = await brand_factory(name="Nike")

    product = await product_factory(
        name="Phone",
        price=1000,
        category_id=category.id,
        brand_id=brand.id,
    )

    category_id = category.id
    product_id = product.id

    await db_session.commit()

    response = await client.delete(
        f"/api/v1/admin/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

    db_session.expire_all()

    assert await db_session.get(Category, category_id) is not None
    assert await db_session.get(Products, product_id) is not None


async def test_admin_delete_brand(
    client, admin_headers, brand_factory, db_session
):
    brand = await brand_factory(name="Nike")
    brand_id = brand.id

    response = await client.delete(
        f"/api/v1/admin/brands/{brand_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()
    assert await db_session.get(Brands, brand_id) is None


async def test_admin_cannot_delete_brand_with_products(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Electronics")

    product = await product_factory(
        name="Phone",
        price=1000,
        brand_id=brand.id,
        category_id=category.id,
    )

    brand_id = brand.id
    product_id = product.id

    await db_session.commit()

    response = await client.delete(
        f"/api/v1/admin/brands/{brand_id}",
        headers=admin_headers,
    )

    assert response.status_code == 409

    db_session.expire_all()

    assert await db_session.get(Brands, brand_id) is not None
    assert await db_session.get(Products, product_id) is not None


async def test_admin_create_product(
    client, admin_headers, brand_factory, category_factory, db_session
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    response = await client.post(
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

    product = await db_session.get(Products, data["id"])
    assert product is not None
    assert product.name == "Air Max"


async def test_admin_partial_update_product(
    client, admin_headers, product_factory,
    brand_factory, category_factory, db_session
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    product = await product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    response = await client.patch(
        f"/api/v1/admin/products/{product.id}",
        headers=admin_headers,
        json={"price": 200},
    )

    assert response.status_code == 200

    await db_session.refresh(product)

    assert float(product.price) == 200
    assert product.name == "Air Max"
    assert product.description == "Test product"


@pytest.mark.parametrize("price", [0, -1, -100])
async def test_admin_cannot_create_product_with_invalid_price(
    client, admin_headers, brand_factory, category_factory, price
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    response = await client.post(
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


async def test_hidden_product_visibility(
    client, admin_headers, product_factory,
    brand_factory, category_factory
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    product = await product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
        is_visible=False,
    )

    public_response = await client.get("/api/v1/products")

    admin_response = await client.get(
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
async def test_admin_cannot_update_product_with_invalid_price(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
    price,
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    product = await product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    response = await client.patch(
        f"/api/v1/admin/products/{product.id}",
        headers=admin_headers,
        json={"price": price},
    )

    assert response.status_code == 422

    await db_session.refresh(product)
    assert float(product.price) == 150


async def test_admin_soft_delete_product(
    client,
    admin_headers,
    brand_factory,
    category_factory,
    product_factory,
    db_session,
):
    brand = await brand_factory(name="Nike")
    category = await category_factory(name="Shoes")

    product = await product_factory(
        name="Air Max",
        price=150,
        brand_id=brand.id,
        category_id=category.id,
    )

    product_id = product.id

    response = await client.delete(
        f"/api/v1/admin/products/{product_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    db_session.expire_all()

    saved_product = await db_session.get(Products, product_id)

    assert saved_product is not None
    assert saved_product.is_visible is False

    public_response = await client.get("/api/v1/products")
    admin_response = await client.get(
        "/api/v1/admin/products",
        headers=admin_headers,
    )

    assert public_response.status_code == 200
    assert admin_response.status_code == 200

    public_ids = [p["id"] for p in public_response.json()]
    admin_ids = [p["id"] for p in admin_response.json()]

    assert product_id not in public_ids
    assert product_id in admin_ids


async def test_admin_create_info(client, admin_headers, db_session):
    response = await client.post(
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

    record = await db_session.get(Info, "about")

    assert record is not None
    assert record.info == "About our shop"

    public_response = await client.get("/api/v1/info")

    assert public_response.status_code == 200
    assert any(
        item["slug"] == "about"
        for item in public_response.json()
    )


async def test_admin_update_info(client, admin_headers, db_session):
    record = Info(
        slug="about",
        info="Old information",
        owners="Timofei",
        contacts="old@example.com",
    )
    db_session.add(record)
    await db_session.flush()

    response = await client.patch(
        "/api/v1/admin/info/about",
        headers=admin_headers,
        json={"info": "New information"},
    )

    assert response.status_code == 200

    await db_session.refresh(record)

    assert record.info == "New information"
    assert record.owners == "Timofei"
    assert record.contacts == "old@example.com"


async def test_hidden_info_not_public(client, admin_headers, db_session):
    record = Info(
        slug="secret",
        info="Private information",
        owners="Timofei",
        contacts="private@example.com",
        is_visible=False,
    )
    db_session.add(record)
    await db_session.flush()

    response = await client.get("/api/v1/info")

    assert response.status_code == 200
    assert all(
        item["slug"] != "secret"
        for item in response.json()
    )

    assert await db_session.get(Info, "secret") is not None


async def test_admin_create_user(client, admin_headers, db_session):
    response = await client.post(
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

    user = await db_session.get(User, data["id"])

    assert user is not None
    assert user.password_hash != "Test12345!"
    assert user.is_active is True


async def test_regular_user_cannot_create_user(
    client, regular_user_headers, db_session
):
    response = await client.post(
        "/api/v1/admin/users",
        headers=regular_user_headers,
        json={
            "username": "blocked123",
            "password": "Test12345!",
            "nickname": "Blocked",
        },
    )

    assert response.status_code == 403

    stmt = select(User).where(
        User.username == "blocked123"
    ).limit(1)

    result = await db_session.execute(stmt)
    user = result.scalars().first()

    assert user is None
