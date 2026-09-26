from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.image import Images


def get_images(db: Session) -> list[Images]:
    return db.query(Images).filter(Images.is_visible == True).all()


def create_image(
    db: Session,
    product_id: int,
    key: str,
):
    image = Images(
        product_id=product_id,
        key=key,
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


def get_image(db: Session, image_id: int, product_id: int) -> Images:
    image = db.query(Images).filter(
        Images.id == image_id,
        product_id == product_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )
    return db.get(Images, image_id)


def delete_image(db: Session, image_obj: Images):
    db.delete(image_obj)
    db.commit()
    return image_obj
