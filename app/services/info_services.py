from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import info
from app.storage import info as info_storage


async def get_info(db: AsyncSession):
    return await info_storage.get_info(db)


async def add_info(data: info.InfoAdd, db: AsyncSession):
    return await info_storage.add_info(db, data)


async def update_info(slug: str, data: info.InfoUpdate, db: AsyncSession):
    return await info_storage.update_info(db=db, slug=slug, data=data)
