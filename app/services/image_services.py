import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from app.services.product_services import get_product_by_id
from app.storage import image, r2
from app.schemas import image as image_schema
from app.core.config import settings


ALLOWED_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}


def create_presigned_upload(data: image_schema.ImagePresignRequest):
    if data.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail="Invalid content type",
        )
    extension = ALLOWED_TYPES[data.content_type]
    key = f"products/{uuid.uuid4()}.{extension}"

    upload_url = r2.create_presigned_put(key, data.content_type)
    return image_schema.ImagePresignResponse(
        upload_url=upload_url,
        key=key,
    )


def register_image(
        db: Session,
        data: image_schema.ImageCreate,
):
    if not data.key.startswith("products/"):
        raise HTTPException(
            status_code=422,
            detail="Invalid key",
        )

    try:
        object_info = r2.get_object_info(data.key)
    except ClientError:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )
    if object_info["ContentType"] not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail="Invalid content type",
        )
    if object_info["ContentLength"] > settings.image_max_size:
        raise HTTPException(
            status_code=422,
            detail="Image is too big",
        )
    if not data.key.startswith("products/"):
        raise HTTPException(
            status_code=422,
            detail="Invalid key",
        )

    get_product_by_id(db, data.product_id)
    return image.create_image(db, data.product_id, data.key)


def get_images(db: Session):
    return image.get_images(db)


def delete_image(db: Session, image_id: int):
    image_obj = image.get_image(db, image_id)

    if not image_obj:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    r2.delete_object(image_obj.key)
    return image.delete_image(db, image_obj)
