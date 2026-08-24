from sqlalchemy.orm import Session

from fastapi import HTTPException
from app.storage import info as info_storage
from app.storage import info as category_storage
from app.storage import info as brand_storage
from app.storage import info as product_storage
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

def get_brands():
    db = SessionLocal()
    try:
        return brand_storage.get_brands(db)
    finally:
        db.close()

def get_products():
    db = SessionLocal()
    try:
        return product_storage.get_products(db)
    finally:
        db.close()
