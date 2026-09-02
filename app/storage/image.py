from sqlalchemy.orm import Session

from app.models.product import Images


def get_images(db: Session) -> list[Images]:
    return db.query(Images).all()
