from database import SessionLocal

from app.storage import category as category_storage
from app.schemas.category import CategoryUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_categories(db: Session):

    return category_storage.get_categories(db)


def add_category(data, db):
    return category_storage.create_category(db, data)


def delete_category(
        db: Session,
        category_id: int,
):
    return category_storage.delete_category(db, category_id)


def update_category(
        db: Session,
        category_id: int,
        data: CategoryUpdate
):
    category = category_storage.update_category(db, category_id, data)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category
