from fastapi import HTTPException

from app.storage import product as product_storage
from app.schemas import product
from sqlalchemy.orm import Session


def get_product_by_id(db: Session, product_id: int):
    product = product_storage.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def get_products(
    db: Session,
    category_id: int | None = None,
    brand_id: int | None = None,
):
    return product_storage.get_products(
        db,
        category_id=category_id,
        brand_id=brand_id,
    )


def add_product(db: Session, data: product.ProductCreate):
    return product_storage.create_product(db, data)


def get_product_by_id_admin(db: Session, product_id: int):
    return product_storage.get_product_by_id_admin(db, product_id)


def get_product_admin(db: Session):
    return product_storage.get_product_admin(db)


def update_product_visibility(db: Session, product_id: int, data: product.ProductVisibilityUpdate):
    product = product_storage.update_product_visibility(db, product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def edit_product(db: Session, product_id: int, data: product.ProductEdit):
    product = product_storage.edit_product(db, product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
