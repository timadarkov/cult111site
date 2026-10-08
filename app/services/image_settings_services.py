from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import image_settings
from app.storage import image_settings as image_settings_storage


def update_main_image(
    db: Session,
    product_id: int,
    data: image_settings.ImageMainUpdate,
):
    product = image_settings_storage.get_product_for_image_update(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    images = image_settings_storage.get_product_images(db, product_id)
    if not any(image.id == data.image_id and image.is_visible for image in images):
        raise HTTPException(status_code=404, detail="Image not found")

    image_settings_storage.update_main_image(
        db=db,
        images=images,
        image_id=data.image_id,
    )


def update_image_order(
    db: Session,
    product_id: int,
    data: image_settings.ImageOrderUpdate,
):
    if len(data.image_ids) != len(set(data.image_ids)):
        raise HTTPException(status_code=422, detail="Duplicate image IDs")

    product = image_settings_storage.get_product_for_image_update(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    images = image_settings_storage.get_product_images(db, product_id)
    visible_images = [image for image in images if image.is_visible]
    if set(data.image_ids) != {image.id for image in visible_images}:
        raise HTTPException(
            status_code=422,
            detail="Provide all visible image IDs belonging to this product",
        )

    image_settings_storage.update_image_order(
        db=db,
        images=visible_images,
        image_ids=data.image_ids,
    )
