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


def get_image(db: Session, image_id: int):
    return db.get(Images, image_id)


def delete_image(db: Session, image: Images):
    db.delete(image)
    db.commit()
