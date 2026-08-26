
from http.client import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from app.models.db import Products



def get_products(db : Session) -> list[Products]:
    return db.query(Products).options(selectinload(Products.images)).all()


def get_product_by_id(db : Session, id: int) -> Products:

    product = db.query(Products).options(selectinload(Products.images)).filter(Products.id == id).first()
    return product

def get_products_by_category(db: Session, category_id: int) -> list[Products]:
    return (db.query(Products).options(selectinload(Products.images)).filter(Products.category_id == category_id).all())

def get_products_by_brand(db: Session, brand_id: int) -> list[Products]:
    return (db.query(Products).options(selectinload(Products.images)).filter(Products.brand_id == brand_id).all())