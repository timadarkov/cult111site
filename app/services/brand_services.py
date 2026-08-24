from database import SessionLocal

from app.storage import brand as brand_storage






def get_brands():
    db = SessionLocal()
    try:
        return brand_storage.get_brands(db)
    finally:
        db.close()
