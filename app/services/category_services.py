from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Products
from app.schemas import category
from app.storage import category as category_storage


async def get_categories(db: AsyncSession):

    return await category_storage.get_categories(db)


async def get_categories_admin(db: AsyncSession):
    return await category_storage.get_category_for_admin(db)


async def add_category(db: AsyncSession, data: category.CategoryCreate):
    try:
        new_category = category_storage.create_category(db, data)
        await db.commit()
        await db.refresh(new_category)
        return new_category
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )


async def delete_category(db: AsyncSession, category_id: int):
    category = await db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    stmt = select(Products.id).filter(
        Products.category_id == category_id
    ).limit(1)
    result = await db.execute(stmt)
    has_products = result.scalars().first()

    if has_products is not None:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category with products",
        )

    return await category_storage.delete_category(db, category_id)


async def edit_category(db: AsyncSession, category_id: int, data: category.CategoryEdit):
    try:
        updated_category = await category_storage.edit_category(
            db, category_id, data
        )
    except IntegrityError:
        await db.rollback()
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


async def update_category_visibility(db: AsyncSession, category_id: int, data: category.CategoryVisibilityUpdate):
    category = await category_storage.update_category_visibility(
        db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
