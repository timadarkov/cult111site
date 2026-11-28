from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image import Images
from app.storage import r2


async def get_image_for_copy(db: AsyncSession, image_id: int) -> Images | None:
    stmt = select(Images).where(
        Images.id == image_id,
        Images.is_visible.is_(True),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def copy_image_file(source_key: str, key: str):
    await r2.copy_object(source_key, key)


async def delete_image_file(key: str):
    await r2.delete_object(key)


async def create_image_copy(
    db: AsyncSession,
    product_id: int,
    key: str,
    position: int,
    is_main: bool,
) -> Images:
    image = Images(
        product_id=product_id,
        key=key,
        position=position,
        is_main=is_main,
    )
    db.add(image)
    await db.flush()
    return image
