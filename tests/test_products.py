from decimal import Decimal

from app.models.brand import Brands
from app.models.category import Category
from app.models.product import Products
from app.models.image import Images


def create_brand(db_session, name, is_visible=True):

    brand = Brands(name=name, is_visible=is_visible)

    db_session.add(brand)
    db_session.flush()

    return brand


def create_category(db_session, name, is_visible=True):

    category = Category(name=name, is_visible=is_visible)

    db_session.add(category)
    db_session.flush()

    return category


def create_product(db_session, name, price, category_id, brand_id, is_visible=True):

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


def test_hidden_product_not_in_list(client, db_session):

    testbrand = create_brand(
        db_session,
        name="Test",
        is_visible=True,
    )

    testcategory = create_category(
        db_session,
        name="Test",
        is_visible=True
    )

    not_visible_product = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=testcategory.id,
        brand_id=testbrand.id,
        is_visible=False
    )

    visible_product = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=testcategory.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    response = client.get("/api/v1/products")
    products = response.json()

    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert visible_product.id in returned_ids
    assert not_visible_product.id not in returned_ids


def test_hidden_product_not_accessible_by_id(client, db_session):

    testbrand = create_brand(
        db_session,
        name="Test",
        is_visible=True,
    )

    testcategory = create_category(
        db_session,
        name="Test",
        is_visible=True
    )

    not_visible_product = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=testcategory.id,
        brand_id=testbrand.id,
        is_visible=False
    )

    response = client.get(f"/api/v1/products/{not_visible_product.id}")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Product not found"


def test_get_nonexistent_product(client):

    response = client.get("/api/v1/products/99999999")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Product not found"


def test_get_product_with_images(client, db_session):

    testbrand = create_brand(
        db_session,
        name="Test",
        is_visible=True,
    )

    testcategory = create_category(
        db_session,
        name="Test",
        is_visible=True
    )

    product_test = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=testcategory.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    test_image = Images(
        product_id=product_test.id,
        key="products/test-image-1.jpg",
        position=0,
        is_main=True
    )
    test_image2 = Images(
        product_id=product_test.id,
        key="products/test-image-2.jpg",
        position=1,
        is_main=False
    )

    db_session.add_all([test_image, test_image2])
    db_session.flush()

    response = client.get(f"/api/v1/products/{product_test.id}")
    product = response.json()
    images = product["images"]
    returned_keys = [image["key"] for image in images]
    images_by_key = {image["key"]: image for image in images}

    first_image = images_by_key[test_image.key]
    second_image = images_by_key[test_image2.key]

    assert response.status_code == 200
    assert product["id"] == product_test.id
    assert product["name"] == product_test.name
    assert len(images) == 2
    assert test_image.key in returned_keys
    assert test_image2.key in returned_keys

    assert first_image["id"] == test_image.id
    assert first_image["position"] == test_image.position
    assert first_image["is_main"] == test_image.is_main
    assert first_image["product_id"] == product_test.id
    assert first_image["url"].endswith(test_image.key)

    assert second_image["id"] == test_image2.id
    assert second_image["position"] == test_image2.position
    assert second_image["is_main"] == test_image2.is_main
    assert second_image["product_id"] == product_test.id
    assert second_image["url"].endswith(test_image2.key)


def test_filter_products_by_category(client, db_session):

    testbrand = create_brand(
        db_session,
        name="Test",
        is_visible=True,
    )

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=True
    )

    category2 = create_category(
        db_session,
        name="Shoes",
        is_visible=True
    )

    product1 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    product2 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    product3 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?category_id={category1.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert product1.id in returned_ids
    assert product2.id not in returned_ids
    assert product3.id not in returned_ids


def test_filter_products_by_brand(client, db_session):

    brand1 = create_brand(
        db_session,
        name="nide",
        is_visible=True,
    )

    brand2 = create_brand(
        db_session,
        name="aabibas",
        is_visible=True,
    )

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=True
    )

    category2 = create_category(
        db_session,
        name="Shoes",
        is_visible=True
    )

    product1 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand1.id,
        is_visible=True
    )

    product2 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=brand1.id,
        is_visible=True
    )

    product3 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=brand2.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?brand_id={brand1.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert product1.id in returned_ids
    assert product2.id in returned_ids
    assert product3.id not in returned_ids


def test_filter_products_by_brand_and_category(client, db_session):

    brand1 = create_brand(
        db_session,
        name="nide",
        is_visible=True,
    )

    brand2 = create_brand(
        db_session,
        name="aabibas",
        is_visible=True,
    )

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=True
    )

    category2 = create_category(
        db_session,
        name="Shoes",
        is_visible=True
    )

    product1 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand1.id,
        is_visible=True
    )

    product2 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=brand1.id,
        is_visible=True
    )

    product3 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand2.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?category_id={category1.id}&brand_id={brand1.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert product1.id in returned_ids
    assert product2.id not in returned_ids
    assert product3.id not in returned_ids


def test_product_of_hidden_brand(client, db_session):

    brand1 = create_brand(
        db_session,
        name="nide",
        is_visible=False,
    )

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=True
    )

    product1 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand1.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?brand_id={brand1.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert product1.id in returned_ids


def test_product_of_hidden_category(client, db_session):

    brand1 = create_brand(
        db_session,
        name="nide",
        is_visible=True,
    )

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=False
    )

    product1 = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand1.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?category_id={category1.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert product1.id in returned_ids


def test_get_visible_brands(client, db_session):

    brand1 = create_brand(
        db_session,
        name="nidel",
        is_visible=True,
    )
    brand2 = create_brand(
        db_session,
        name="nid",
        is_visible=True,
    )
    brand3 = create_brand(
        db_session,
        name="ni",
        is_visible=False,
    )

    response = client.get(
        "/api/v1/brands"
    )
    brands = response.json()

    returned_ids = [item["id"] for item in brands]

    assert response.status_code == 200
    assert brand1.id in returned_ids
    assert brand2.id in returned_ids
    assert brand3.id not in returned_ids


def test_get_visible_categories(client, db_session):

    category1 = create_category(
        db_session,
        name="Clothes",
        is_visible=False
    )
    category2 = create_category(
        db_session,
        name="Clothes1",
        is_visible=False
    )
    category3 = create_category(
        db_session,
        name="Clothes2",
        is_visible=True
    )

    response = client.get(
        "/api/v1/categories"
    )
    categories = response.json()

    returned_ids = [item["id"] for item in categories]

    assert response.status_code == 200
    assert category1.id not in returned_ids
    assert category2.id not in returned_ids
    assert category3.id in returned_ids


def test_get_existing_product(client, db_session):

    testbrand = create_brand(
        db_session,
        name="Test",
        is_visible=True,
    )

    testcategory = create_category(
        db_session,
        name="Test",
        is_visible=True
    )

    product_test = create_product(
        db_session,
        name="Test t-shirt",
        price=100,
        category_id=testcategory.id,
        brand_id=testbrand.id,
        is_visible=True
    )

    response = client.get(f"/api/v1/products/{product_test.id}")
    product = response.json()

    assert response.status_code == 200
    assert product["id"] == product_test.id
    assert product["name"] == product_test.name
    assert product["price"] == product_test.price


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
