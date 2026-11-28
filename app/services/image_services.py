import uuid

from botocore.exceptions import ClientError
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas import image as image_schema
from app.services.product_services import get_product_by_id
from app.storage import image, r2

ALLOWED_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}


async def create_presigned_upload(data: image_schema.ImagePresignRequest):
    if data.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail="Invalid content type",
        )

    extension = ALLOWED_TYPES[data.content_type]
    key = f"products/{uuid.uuid4()}.{extension}"

    upload_url = await r2.create_presigned_put(key, data.content_type)

    return image_schema.ImagePresignResponse(
        upload_url=upload_url,
        key=key,
    )


async def register_image(
        db: AsyncSession,
        data: image_schema.ImageCreate,
        product_id: int,
):
    if not data.key.startswith("products/"):
        raise HTTPException(
            status_code=422,
            detail="Invalid key",
        )

    try:
        object_info = await r2.get_object_info(data.key)
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

    await get_product_by_id(db, product_id)
    return await image.create_image(db, product_id, data.key)


async def get_images(db: AsyncSession):
    return await image.get_images(db)


async def delete_image(
    db: AsyncSession,
    image_id: int,
    product_id: int,
):
    image_obj = await image.get_image(db, image_id, product_id)

    if not image_obj:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    await r2.delete_object(image_obj.key)

    return await image.delete_image(
        db,
        image_obj=image_obj,
    )
