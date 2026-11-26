import logging
import uuid
from pathlib import PurePosixPath

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import image_copy
from app.storage import image_copy as image_copy_storage
from app.storage import image_settings as image_settings_storage

logger = logging.getLogger(__name__)


async def copy_product_image(
    db: AsyncSession,
    product_id: int,
    data: image_copy.ImageCopyRequest,
):
    product = await image_settings_storage.get_product_for_image_update(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    source = await image_copy_storage.get_image_for_copy(db, data.image_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Image not found")
    if source.product_id == product_id:
        raise HTTPException(status_code=409, detail="Image already belongs to this product")

    images = await image_settings_storage.get_product_images(db, product_id)
    visible_images = [image for image in images if image.is_visible]
    position = max((image.position or 0 for image in visible_images), default=-1) + 1
    key = f"products/{uuid.uuid4()}{PurePosixPath(source.key).suffix}"

    try:
        image_copy_storage.copy_image_file(source.key, key)
    except Exception as error:
        await db.rollback()
        raise HTTPException(status_code=502, detail="Could not copy image in storage") from error

    try:
        image = await image_copy_storage.create_image_copy(
            db=db,
            product_id=product_id,
            key=key,
            position=position,
            is_main=not visible_images,
        )
        result = image_copy.ImageCopyResponse.model_validate(image)
        await db.commit()
    except Exception:
        await db.rollback()
        try:
            image_copy_storage.delete_image_file(key)
        except Exception:
            logger.exception("Could not remove unused image copy: %s", key)
        raise

    return result
