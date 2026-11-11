import pytest
from uuid import UUID
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.image import Images


@pytest.mark.parametrize(
    "content_type, extension",
    [
        ("image/png", "png"),
        ("image/jpeg", "jpg"),
        ("image/webp", "webp"),
    ],
)
def test_presign_allowed_types(
    client, admin_headers, r2_mock, content_type, extension,
):
    response = client.post(
        "/api/v1/admin/images/presign",
        headers=admin_headers,
        json={"content_type": content_type},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["upload_url"] == "https://storage.test/upload"

    key = data["key"]
    assert key.startswith("products/")
    assert key.endswith(f".{extension}")

    filename = key.removeprefix("products/").removesuffix(f".{extension}")
    UUID(filename)

    r2_mock.generate_presigned_url.assert_called_once_with(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )


def test_presign_invalid_type(
    client, admin_headers, r2_mock,
):

    response = client.post(
        "/api/v1/admin/images/presign",
        headers=admin_headers,
        json={"content_type": "text/plain"},
    )

    assert response.status_code == 422

    r2_mock.generate_presigned_url.assert_not_called()


def test_presign_forbidden_for_regular_user(
    client, regular_user_headers, r2_mock,
):

    response = client.post(
        "/api/v1/admin/images/presign",
        headers=regular_user_headers,
        json={"content_type": "image/png"},
    )

    assert response.status_code == 403

    r2_mock.generate_presigned_url.assert_not_called()


def test_presign_unauthorized(
        client, r2_mock,
):

    response = client.post(
        "/api/v1/admin/images/presign",
        json={"content_type": "image/png"},
    )

    assert response.status_code == 401

    r2_mock.generate_presigned_url.assert_not_called()


def test_register_image_invalid_key(
        client, admin_headers, r2_mock
):
    response = client.post(
        "/api/v1/admin/products/1/images",
        headers=admin_headers,
        json={"key": "other/test.png"},
    )

    assert response.status_code == 422

    r2_mock.head_object.assert_not_called()


def test_register_image_not_found(
        client, admin_headers, r2_mock
):

    r2_mock.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not found"}},
        "HeadObject",
    )

    response = client.post(
        "/api/v1/admin/products/1/images",
        headers=admin_headers,
        json={"key": "products/missing.png"},
    )

    assert response.status_code == 404

    r2_mock.head_object.assert_called_once()


def test_register_image_invalid_content_type(
        client, admin_headers, r2_mock
):
    r2_mock.head_object.return_value = {
        "ContentType": "text/plain",
        "ContentLength": 100,
    }

    response = client.post(
        "/api/v1/admin/products/1/images",
        headers=admin_headers,
        json={
            "key": "products/test.txt",
        }
    )

    assert response.status_code == 422

    r2_mock.head_object.assert_called_once()


def test_register_image_too_large(
    client, admin_headers, r2_mock
):
    r2_mock.head_object.return_value = {
        "ContentType": "image/png",
        "ContentLength": settings.image_max_size + 1,
    }

    response = client.post(
        "/api/v1/admin/products/1/images",
        json={"key": "products/large.png"},
        headers=admin_headers,
    )

    assert response.status_code == 422

    r2_mock.head_object.assert_called_once()


def test_register_image_success(
    client,
    admin_headers,
    r2_mock,
    db_session,
    brand_factory,
    category_factory,
    product_factory,
):
    brand = brand_factory(name="test_brand")
    category = category_factory(name="test_cat")
    product = product_factory(name="test_prod", category_id=category.id, brand_id=brand.id, price=1000,)

    response = client.post(
        f"/api/v1/admin/products/{product.id}/images",
        headers=admin_headers,
        json={"key": "products/test.png"},
    )

    assert response.status_code == 201

    r2_mock.head_object.assert_called_once()

    data = response.json()

    saved_image = db_session.query(Images).filter(
        Images.product_id == product.id
    ).first()

    assert data["key"] == "products/test.png"

    assert saved_image is not None
    assert saved_image.product_id == product.id
    assert saved_image.key == "products/test.png"


def test_register_image_forbidden(
    client, regular_user_headers, r2_mock
):
    response = client.post(
        "/api/v1/admin/products/1/images",
        headers=regular_user_headers,
        json={"key": "products/test.png"},
    )

    assert response.status_code == 403

    r2_mock.head_object.assert_not_called()


def test_delete_image_success(
    client,
    admin_headers,
    r2_mock,
    db_session,
    brand_factory,
    category_factory,
    product_factory,
):
    brand = brand_factory(name="test_brand")
    category = category_factory(name="test_cat")
    product = product_factory(name="test_prod", category_id=category.id, brand_id=brand.id, price=1000,)

    image = Images(
        product_id=product.id,
        key="products/test.png",
    )

    db_session.add(image)
    db_session.flush()

    image_id = image.id

    response = client.delete(
        f"/api/v1/admin/products/{product.id}/images/{image.id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    r2_mock.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="products/test.png",
    )
    deleted_image = db_session.get(Images, image_id)

    assert deleted_image is None


def test_delete_image_not_found(
    client,
    admin_headers,
    r2_mock,
):

    response = client.delete(
        "/api/v1/admin/products/999999/images/99999",
        headers=admin_headers,
    )

    assert response.status_code == 404

    r2_mock.delete_object.assert_not_called()


def test_delete_image_wrong_product(
    client,
    admin_headers,
    r2_mock,
    db_session,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory(name="test_brand")
    category = category_factory(name="test_cat")
    product1 = product_factory(name="test_prod1", category_id=category.id, brand_id=brand.id, price=1000,)
    product2 = product_factory(name="test_prod2", category_id=category.id, brand_id=brand.id, price=1000,)

    image = Images(
        product_id=product1.id,
        key="products/test.png",
    )

    db_session.add(image)
    db_session.flush()

    image_id = image.id

    response = client.delete(
        f"/api/v1/admin/products/{product2.id}/images/{image_id}",
        headers=admin_headers,
    )

    assert response.status_code == 404

    r2_mock.delete_object.assert_not_called()

    saved_image = db_session.get(Images, image_id)

    assert saved_image is not None
    assert saved_image.product_id == product1.id


def test_copy_image_success(
    client,
    admin_headers,
    r2_mock,
    db_session,
    brand_factory,
    category_factory,
    product_factory,
):

    brand = brand_factory(name="test_brand")
    category = category_factory(name="test_cat")
    product1 = product_factory(name="test_prod1", category_id=category.id, brand_id=brand.id, price=1000,)
    product2 = product_factory(name="test_prod2", category_id=category.id, brand_id=brand.id, price=1000,)

    image = Images(
        product_id=product1.id,
        key="products/original.png",
    )

    db_session.add(image)
    db_session.flush()

    image_id = image.id

    response = client.post(
        f"/api/v1/admin/products/{product2.id}/images/copy",
        headers=admin_headers,
        json={
            "image_id": image_id
        },
    )

    assert response.status_code == 201

    data = response.json()

    r2_mock.copy_object.assert_called_once_with(
        Bucket="test-bucket",
        CopySource={
            "Bucket": "test-bucket",
            "Key": "products/original.png",
        },
        Key=data["key"],
    )

    copied_image = db_session.query(Images).filter(
        Images.key == data["key"]
    ).first()

    original_image = db_session.get(Images, image_id)

    assert data["product_id"] == product2.id
    assert data["key"] != "products/original.png"

    assert data["key"].startswith("products/")
    assert data["key"].endswith(".png")

    assert copied_image is not None
    assert copied_image.product_id == product2.id
    assert copied_image.key == data["key"]

    assert original_image is not None
    assert original_image.product_id == product1.id
    assert original_image.key == "products/original.png"


def test_copy_image_forbidden(
    client, regular_user_headers, r2_mock
):
    response = client.post(
        "/api/v1/admin/products/1/images/copy",
        headers=regular_user_headers,
        json={
            "image_id": 1
        }
    )

    assert response.status_code == 403

    r2_mock.copy_object.assert_not_called()
