from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brands
from app.models.product import Products
from app.schemas.brand import BrandCreate, BrandEdit, BrandVisibilityUpdate
from app.storage import brand as brand_storage


async def get_brands(db: AsyncSession):
    return await brand_storage.get_brands(db)


async def get_brands_admin(db: AsyncSession):
    return await brand_storage.get_brands_for_admin(db)


async def add_brand(db: AsyncSession, data: BrandCreate):
    try:
        brand = brand_storage.create_brand(db, data)
        await db.commit()
        await db.refresh(brand)
        return brand
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Brand name already exists",
        )


async def update_brand_visibility(db: AsyncSession, brand_id: int, data: BrandVisibilityUpdate):
    return await brand_storage.update_brand_visibility(db, brand_id, data)


async def edit_brand(db: AsyncSession, brand_id: int, data: BrandEdit):
    try:
        return await brand_storage.edit_brand(
            brand_id=brand_id,
            data=data,
            db=db,
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Brand name already exists",
        )


async def delete_brand(db: AsyncSession, brand_id: int):
    brand = await db.get(Brands, brand_id)

    if brand is None:
        raise HTTPException(
            status_code=404,
            detail="Brand not found",
        )

    stmt = select(Products.id).where(
        Products.brand_id == brand_id
    ).limit(1)

    result = await db.execute(stmt)
    has_products = result.scalar_one_or_none()

    if has_products is not None:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete brand with products",
        )

    return await brand_storage.delete_brand(db, brand_id)
