from fastapi import HTTPException

from database import SessionLocal

from app.storage import product as product_storage


def get_product_by_id(product_id: int):
    db = SessionLocal()
    try:
        product = product_storage.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        db.close()


def get_products(
    category_id: int | None = None,
    brand_id: int | None = None,
):
    db = SessionLocal()
    try:
        return product_storage.get_products(
            db,
            category_id=category_id,
            brand_id=brand_id,
        )
    finally:
        db.close()
