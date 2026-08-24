
from sqlalchemy.orm import Session

from app.models.db import Products




def get_products(db : Session) -> list[Products]:
    return db.query(Products).all()
