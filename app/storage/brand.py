from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brands
from app.schemas.brand import BrandCreate, BrandEdit, BrandVisibilityUpdate


async def get_brands(db: AsyncSession) -> list[Brands]:
    stmt = select(Brands).where(Brands.is_visible.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_brands_for_admin(
    db:  AsyncSession,
    is_visible: bool | None = None,
) -> list[Brands]:

    stmt = select(Brands)

    if is_visible is not None:
        stmt = stmt.where(Brands.is_visible.is_(is_visible))

    result = await db.execute(stmt)
    return list(result.scalars().all())


def create_brand(db: AsyncSession, data: BrandCreate):
    brand = Brands(
        name=data.name,
        is_visible=data.is_visible,
    )
    db.add(brand)
    return brand


async def update_brand_visibility(
    db: AsyncSession,
    brand_id: int,
    data: BrandVisibilityUpdate,
) -> Brands | None:
    brand = await db.get(Brands, brand_id)

    if not brand:
        return None

    brand.is_visible = data.is_visible

    await db.commit()
    await db.refresh(brand)

    return brand


async def edit_brand(
    db: AsyncSession,
    brand_id: int,
    data: BrandEdit,
) -> Brands | None:
    brand = await db.get(Brands, brand_id)

    if not brand:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(brand, field, value)

    await db.commit()
    await db.refresh(brand)

    return brand


async def delete_brand(db: AsyncSession, brand_id: int):
    brand = await db.get(Brands, brand_id)

    if brand is None:
        return None

    await db.delete(brand)
    await db.commit()

    return brand
