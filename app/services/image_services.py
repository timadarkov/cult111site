from database import SessionLocal

from app.storage import image as image_storage






def get_images():
    db = SessionLocal()
    try:
        return image_storage.get_images(db)
    finally:
        db.close()
