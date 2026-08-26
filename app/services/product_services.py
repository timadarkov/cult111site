from http.client import HTTPException

from database import SessionLocal

from app.storage import product as product_storage






def get_products():
    db = SessionLocal()
    try:
        return product_storage.get_products(db)
    finally:
        db.close()

def get_product_by_id(product_id: int):
    db = SessionLocal()
    try:
        product = product_storage.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        db.close()

def get_products_by_category(category_id: int):
    db = SessionLocal()
    try:
        products = product_storage.get_products_by_category(db, category_id)
        return products
    finally:
        db.close()

def get_products_by_brand(brand_id: int):
    db = SessionLocal()
    try:
        products = product_storage.get_products_by_brand(db, brand_id)
        return products
    finally:
        db.close()