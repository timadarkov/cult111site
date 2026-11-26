
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Products
from app.schemas import product


async def get_products(db: AsyncSession, category_id: int | None = None, brand_id: int | None = None) -> list[Products]:

    stmt = select(Products).options(selectinload(
        Products.images)).where(Products.is_visible.is_(True))

    if category_id:

        stmt = stmt.where(Products.category_id == category_id)

    if brand_id:

        stmt = stmt.where(Products.brand_id == brand_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_product_by_id(db: AsyncSession, id: int) -> Products | None:
    return (
        await db.execute(
            select(Products)
            .options(selectinload(Products.images))
            .where(Products.id == id)
            .where(Products.is_visible.is_(True))
        )
    ).scalars().first()


async def get_product_by_id_admin(
    db: AsyncSession,
    product_id: int,
) -> Products | None:
    return (
        await db.execute(
            select(Products)
            .options(selectinload(Products.images))
            .where(Products.id == product_id)
        )
    ).scalars().first()


async def get_product_admin(db: AsyncSession) -> list[Products]:
    stmt = select(Products).options(selectinload(Products.images))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_product(db: AsyncSession, data: product.ProductCreate):
    product = Products(
        name=data.name,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        brand_id=data.brand_id,
    )

    db.add(product)
    await db.commit()
    await db.refresh(
        product,
        attribute_names=[
            "id",
            "name",
            "price",
            "description",
            "category_id",
            "brand_id",
            "is_visible",
            "images",
        ],
    )
    return product


async def update_product_visibility(
    db: AsyncSession,
    product_id: int,
    data: product.ProductVisibilityUpdate,
) -> Products | None:
    product = await db.get(Products, product_id)

    if not product:
        return None

    product.is_visible = data.is_visible

    await db.commit()
    await db.refresh(
        product,
        attribute_names=[
            "id",
            "name",
            "price",
            "description",
            "category_id",
            "brand_id",
            "is_visible",
            "images",
        ],
    )
    return product


async def edit_product(db: AsyncSession, product_id: int, data: product.ProductEdit) -> Products | None:
    product = await db.get(Products, product_id)

    if not product:
        return None

    changes = data.model_dump(
        exclude_unset=True,
        exclude={"images"},
    )

    for field, value in changes.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(
        product,
        attribute_names=[
            "id",
            "name",
            "price",
            "description",
            "category_id",
            "brand_id",
            "is_visible",
            "images",
        ],
    )
    return product


async def delete_product(db: AsyncSession, product_id: int):
    product = await db.get(Products, product_id)

    if product is None:
        return None

    product.is_visible = False

    await db.commit()
    await db.refresh(product)

    return product
