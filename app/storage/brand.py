
from sqlalchemy.orm import Session

from app.models.db import Brands




def get_brands(db : Session) -> list[Brands]:
    return db.query(Brands).all()
