from sqlalchemy.orm import Session

from app.models.db import Category





def get_categories(db : Session) -> list[Category]:
    return db.query(Category).all()
