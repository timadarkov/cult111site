from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image import Images
from app.models.product import Products


async def get_product_for_image_update(
    db: AsyncSession,
    product_id: int,
) -> Products | None:
    stmt = select(Products).where(
        Products.id == product_id
    ).with_for_update()

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_images(db: AsyncSession, product_id: int) -> list[Images]:
    stmt = select(Images).where(
        Images.product_id == product_id,
    ).order_by(Images.position, Images.id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_main_image(db: AsyncSession, images: list[Images], image_id: int):
    for image in images:
        image.is_main = image.id == image_id

    await db.commit()


async def update_image_order(db: AsyncSession, images: list[Images], image_ids: list[int]):
    positions = {image_id: position for position, image_id in enumerate(image_ids)}

    for image in images:
        image.position = positions[image.id]

    await db.commit()
