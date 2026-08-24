from sqlalchemy.orm import Session

from app.models.db import Images





def get_images(db : Session) -> list[Images]:
    return db.query(Images).all()
