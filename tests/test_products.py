from decimal import Decimal
from app.models.image import Images


def test_hidden_product_not_in_list(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    producttest2 = product_factory(
        name="Test t-shirt2",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=False
    )

    response = client.get("/api/v1/products")
    products = response.json()

    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids
    assert producttest2.id not in returned_ids


def test_hidden_product_not_accessible_by_id(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=False
    )

    response = client.get(f"/api/v1/products/{producttest.id}")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Product not found"


def test_get_nonexistent_product(client):

    response = client.get("/api/v1/products/99999999")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Product not found"


def test_get_product_with_images(
    db_session,
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    test_image = Images(
        product_id=producttest.id,
        key="products/test-image-1.jpg",
        position=0,
        is_main=True
    )
    test_image2 = Images(
        product_id=producttest.id,
        key="products/test-image-2.jpg",
        position=1,
        is_main=False
    )

    db_session.add_all([test_image, test_image2])
    db_session.flush()

    response = client.get(f"/api/v1/products/{producttest.id}")
    product = response.json()
    images = product["images"]
    returned_keys = [image["key"] for image in images]
    images_by_key = {image["key"]: image for image in images}

    first_image = images_by_key[test_image.key]
    second_image = images_by_key[test_image2.key]

    assert response.status_code == 200
    assert product["id"] == producttest.id
    assert product["name"] == producttest.name
    assert len(images) == 2
    assert test_image.key in returned_keys
    assert test_image2.key in returned_keys

    assert first_image["id"] == test_image.id
    assert first_image["position"] == test_image.position
    assert first_image["is_main"] == test_image.is_main
    assert first_image["product_id"] == producttest.id
    assert first_image["url"].endswith(test_image.key)

    assert second_image["id"] == test_image2.id
    assert second_image["position"] == test_image2.position
    assert second_image["is_main"] == test_image2.is_main
    assert second_image["product_id"] == producttest.id
    assert second_image["url"].endswith(test_image2.key)


def test_filter_products_by_category(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    category2 = category_factory("sshirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    producttest2 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )
    producttest3 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category2.id,
        brand_id=brand.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?category_id={category.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids
    assert producttest2.id in returned_ids
    assert producttest3.id not in returned_ids


def test_filter_products_by_brand(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    brand1 = brand_factory("Nikes")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    producttest2 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )
    producttest3 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand1.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?brand_id={brand.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids
    assert producttest2.id in returned_ids
    assert producttest3.id not in returned_ids


def test_filter_products_by_brand_and_category(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    brand1 = brand_factory("Nikes")

    category = category_factory("t-shirt")

    category1 = category_factory("sshirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    producttest2 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category1.id,
        brand_id=brand.id,
        is_visible=True
    )
    producttest3 = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand1.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?category_id={category.id}&brand_id={brand.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids
    assert producttest2.id not in returned_ids
    assert producttest3.id not in returned_ids


def test_product_of_hidden_brand(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike", is_visible=False)

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )

    response = client.get(
        f"/api/v1/products?brand_id={brand.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids


def test_product_of_hidden_category(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt", is_visible=False)

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
        is_visible=True
    )
    response = client.get(
        f"/api/v1/products?category_id={category.id}"
    )

    products = response.json()
    returned_ids = [item["id"] for item in products]

    assert response.status_code == 200
    assert producttest.id in returned_ids


def test_get_visible_brands(client, brand_factory):

    brand1 = brand_factory("Nike")

    brand2 = brand_factory("Puma")

    brand3 = brand_factory("Nike", is_visible=False)

    response = client.get(
        "/api/v1/brands"
    )
    brands = response.json()

    returned_ids = [item["id"] for item in brands]

    assert response.status_code == 200
    assert brand1.id in returned_ids
    assert brand2.id in returned_ids
    assert brand3.id not in returned_ids


def test_get_visible_categories(client, category_factory):

    category1 = category_factory("t-shirt",)

    category2 = category_factory("t-shirt",)

    category3 = category_factory("t-shirt", is_visible=False)

    response = client.get(
        "/api/v1/categories"
    )
    categories = response.json()

    returned_ids = [item["id"] for item in categories]

    assert response.status_code == 200
    assert category1.id in returned_ids
    assert category2.id in returned_ids
    assert category3.id not in returned_ids


def test_get_existing_product(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
    )
    response = client.get(f"/api/v1/products/{producttest.id}")
    product = response.json()

    assert response.status_code == 200
    assert product["id"] == producttest.id
    assert product["name"] == producttest.name
    assert product["price"] == producttest.price


def test_get_products(
    client,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory("Nike")

    category = category_factory("t-shirt")

    producttest = product_factory(
        name="Test t-shirt",
        price=100,
        category_id=category.id,
        brand_id=brand.id,
    )

    product_id = producttest.id

    # Act — действие
    response = client.get("/api/v1/products")

    # Assert — проверка
    assert response.status_code == 200

    products = response.json()

    assert any(
        item["id"] == product_id
        and item["name"] == "Test t-shirt"
        for item in products
    )
