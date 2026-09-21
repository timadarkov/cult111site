from sqlalchemy.orm import Session
from app.storage import brand as brand_storage
from app.schemas.brand import BrandAdminResponse, BrandVisibilityUpdate, BrandCreate, BrandEdit


def get_brands(db: Session):
    return brand_storage.get_brands(db)


def get_brands_admin(db: Session):
    return brand_storage.get_brands_for_admin(db)


def add_brand(db: Session, data: BrandCreate):
    return brand_storage.create_brand(db, data)


def update_brand_visibility(db: Session, brand_id: int, data: BrandVisibilityUpdate):
    return brand_storage.update_brand_visibility(db, brand_id, data)


def edit_brand(db: Session, brand_id: int, data: BrandEdit):
    return brand_storage.edit_brand(db, brand_id, data)
