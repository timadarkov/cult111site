from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image import Images


async def get_images(db: AsyncSession) -> list[Images]:
    stmt = select(Images).where(Images.is_visible.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_image(
    db: AsyncSession,
    product_id: int,
    key: str,
):
    image = Images(
        product_id=product_id,
        key=key,
    )

    db.add(image)
    await db.commit()
    await db.refresh(image)

    return image


async def get_image(
    db: AsyncSession,
    image_id: int,
    product_id: int,
) -> Images:
    stmt = select(Images).where(
        Images.id == image_id,
        Images.product_id == product_id,
    )

    result = await db.execute(stmt)
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    return image


async def delete_image(db: AsyncSession, image_obj: Images):
    await db.delete(image_obj)
    await db.commit()
    return image_obj
