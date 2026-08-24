from sqlalchemy.orm import Session

from fastapi import HTTPException
from app.storage import info as info_storage
from app.storage import info as category_storage
from database import SessionLocal



def get_info():
    db = SessionLocal()
    try:
        company = info_storage.get_info(db)   
        return {"info": company.info, "owners": company.owners, "contacts": company.contacts}
    finally:
        db.close()

def get_categories():
    db = SessionLocal()
    try:
        return category_storage.get_categories(db)
    finally:
        db.close()
