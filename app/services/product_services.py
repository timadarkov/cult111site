from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import product
from app.storage import product as product_storage


async def get_product_by_id(db: AsyncSession, product_id: int):
    product = await product_storage.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def get_products(
    db: AsyncSession,
    category_id: int | None = None,
    brand_id: int | None = None,
):
    return await product_storage.get_products(
        db,
        category_id=category_id,
        brand_id=brand_id,
    )


async def add_product(db: AsyncSession, data: product.ProductCreate):
    return await product_storage.create_product(db, data)


async def get_product_by_id_admin(db: AsyncSession, product_id: int):
    return await product_storage.get_product_by_id_admin(db, product_id)


async def get_product_admin(db: AsyncSession):
    return await product_storage.get_product_admin(db)


async def update_product_visibility(db: AsyncSession, product_id: int, data: product.ProductVisibilityUpdate):
    product = await product_storage.update_product_visibility(db, product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def edit_product(db: AsyncSession, product_id: int, data: product.ProductEdit):
    product = await product_storage.edit_product(db, product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def delete_product(db: AsyncSession, product_id: int):
    product = await product_storage.delete_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product
