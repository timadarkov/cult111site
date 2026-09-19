from database import SessionLocal
from sqlalchemy.orm import Session
from app.storage import brand as brand_storage
from app.schemas.brand import BrandAdminResponse, BrandVisibilityUpdate


def get_brands(db: Session):
    return brand_storage.get_brands(db)


def get_brands_admin(db: Session):
    return brand_storage.get_brands_for_admin(db)


def delete_brand(db: Session, brand_id: int, data: BrandVisibilityUpdate):
    return brand_storage.delete_brand(db, brand_id, data)
