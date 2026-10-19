from decimal import Decimal

from app.models.brand import Brands
from app.models.category import Category
from app.models.product import Products


def test_get_products(client, db_session):
    # Arrange — подготовка
    brand = Brands(name="Test Brand")
    category = Category(name="Test Category")

    db_session.add_all([brand, category])
    db_session.flush()

    product = Products(
        name="Test T-Shirt",
        price=Decimal("1500.00"),
        description="Test product",
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True,
    )

    db_session.add(product)
    db_session.flush()

    product_id = product.id

    # Act — действие
    response = client.get("/api/v1/products")

    # Assert — проверка
    assert response.status_code == 200

    products = response.json()

    assert any(
        item["id"] == product_id
        and item["name"] == "Test T-Shirt"
        for item in products
    )
