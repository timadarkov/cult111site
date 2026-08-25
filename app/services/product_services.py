from database import SessionLocal

from app.storage import product as product_storage






def get_products():
    db = SessionLocal()
    try:
        return product_storage.get_products(db)
    finally:
        db.close()
