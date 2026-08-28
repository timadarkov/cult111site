from fastapi import HTTPException

from database import SessionLocal

from app.storage import product as product_storage

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
