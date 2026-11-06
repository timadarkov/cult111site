from sqlalchemy.orm import Session
from app.storage import brand as brand_storage
from app.schemas.brand import BrandAdminResponse, BrandVisibilityUpdate, BrandCreate, BrandEdit
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.brand import Brands
from app.models.product import Products


def get_brands(db: Session):
    return brand_storage.get_brands(db)


def get_brands_admin(db: Session):
    return brand_storage.get_brands_for_admin(db)


def add_brand(db: Session, data: BrandCreate):
    try:
        brand = brand_storage.create_brand(db, data)
        db.commit()
        db.refresh(brand)
        return brand
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Brand name already exists",
        )


def update_brand_visibility(db: Session, brand_id: int, data: BrandVisibilityUpdate):
    return brand_storage.update_brand_visibility(db, brand_id, data)


def edit_brand(db: Session, brand_id: int, data: BrandEdit):
    try:
        return brand_storage.edit_brand(
            brand_id=brand_id,
            data=data,
            db=db,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Brand name already exists",
        )


def delete_brand(db: Session, brand_id: int):
    brand = db.get(Brands, brand_id)

    if brand is None:
        raise HTTPException(
            status_code=404,
            detail="Brand not found",
        )

    has_products = db.query(Products.id).filter(
        Products.brand_id == brand_id
    ).first()

    if has_products:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete brand with products",
        )

    return brand_storage.delete_brand(db, brand_id)
