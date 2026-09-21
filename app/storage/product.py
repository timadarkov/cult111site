from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Products
from app.schemas import product


def get_products(db: Session, category_id: int | None = None, brand_id: int | None = None) -> list[Products]:

    query = db.query(Products).options(selectinload(
        Products.images)).filter(Products.is_visible == True)

    if category_id is not None:

        query = query.filter(Products.category_id == category_id)

    if brand_id is not None:

        query = query.filter(Products.brand_id == brand_id)

    return query.all()


def get_product_by_id(db: Session, id: int) -> Products:

    return (db.query(Products).options(selectinload(Products.images)).filter(Products.id == id).filter(Products.is_visible == True).first())


def create_product(db: Session, data: product.ProductCreate):
    product = Products(
        name=data.name,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        brand_id=data.brand_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
