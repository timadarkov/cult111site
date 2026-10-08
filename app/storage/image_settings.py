from sqlalchemy.orm import Session

from app.models.image import Images
from app.models.product import Products


def get_product_for_image_update(db: Session, product_id: int) -> Products | None:
    return db.query(Products).filter(
        Products.id == product_id,
    ).with_for_update().first()


def get_product_images(db: Session, product_id: int) -> list[Images]:
    return db.query(Images).filter(
        Images.product_id == product_id,
    ).order_by(Images.position, Images.id).all()


def update_main_image(db: Session, images: list[Images], image_id: int):
    for image in images:
        image.is_main = image.id == image_id

    db.commit()


def update_image_order(db: Session, images: list[Images], image_ids: list[int]):
    positions = {image_id: position for position, image_id in enumerate(image_ids)}

    for image in images:
        image.position = positions[image.id]

    db.commit()
