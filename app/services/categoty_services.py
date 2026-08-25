from database import SessionLocal

from app.storage import category as category_storage






def get_categories():
    db = SessionLocal()
    try:
        return category_storage.get_categories(db)
    finally:
        db.close()
