from database import SessionLocal

from app.storage import category as category_storage
from app.schemas import category
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.product import Products
from app.models.category import Category


def get_categories(db: Session):

    return category_storage.get_categories(db)


def get_categories_admin(db: Session):
    return category_storage.get_category_for_admin(db)


def add_category(db: Session, data: category.CategoryCreate):
    try:
        new_category = category_storage.create_category(db, data)
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )


def delete_category(db: Session, category_id: int):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    has_products = db.query(Products.id).filter(
        Products.category_id == category_id
    ).first()

    if has_products:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category with products",
        )

    return category_storage.delete_category(db, category_id)


def edit_category(db: Session, category_id: int, data: category.CategoryEdit):
    try:
        updated_category = category_storage.edit_category(
            db, category_id, data
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )

    if updated_category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return updated_category


def update_category_visibility(db: Session, category_id: int, data: category.CategoryVisibilityUpdate):
    category = category_storage.update_category_visibility(
        db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
