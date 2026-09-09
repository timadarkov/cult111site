from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.product import Products


def get_products(db: Session, category_id: int | None = None, brand_id: int | None = None) -> list[Products]:

    query = db.query(Products).options(selectinload(Products.images))

    if category_id is not None:

        query = query.filter(Products.category_id == category_id)

    if brand_id is not None:

        query = query.filter(Products.brand_id == brand_id)

    return query.all()


def get_product_by_id(db: Session, id: int) -> Products:

    return (db.query(Products).options(selectinload(Products.images)).filter(Products.id == id).first())
