
from sqlalchemy.orm import Session

from app.models.db import Info
from app.models.db import Category


def get_info(db : Session) -> list[Info]:
    return db.query(Info).first()

def get_categories(db : Session) -> list[Category]:
    return db.query(Category).all()


