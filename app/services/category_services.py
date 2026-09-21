from database import SessionLocal

from app.storage import category as category_storage
from app.schemas import category
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_categories(db: Session):

    return category_storage.get_categories(db)


def get_categories_admin(db: Session):
    return category_storage.get_category_for_admin(db)


def add_category(data, db):
    return category_storage.create_category(db, data)


def delete_category(db: Session, category_id: int,):
    return category_storage.delete_category(db, category_id)


def edit_category(db: Session, category_id: int, data: category.CategoryEdit):
    category = category_storage.edit_category(db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def update_category_visibility(db: Session, category_id: int, data: category.CategoryVisibilityUpdate):
    category = category_storage.update_category_visibility(
        db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
