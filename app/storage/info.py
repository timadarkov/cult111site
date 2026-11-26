from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.info import Info
from app.schemas.info import InfoAdd, InfoUpdate


async def get_info(db: AsyncSession) -> list[Info]:
    stmt = select(Info).where(Info.is_visible.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_info(db: AsyncSession, data: InfoAdd):
    info = Info(
        slug=data.slug,
        info=data.info,
        owners=data.owners,
        contacts=data.contacts,
    )

    db.add(info)
    await db.commit()
    await db.refresh(info)
    return info


async def update_info(db: AsyncSession, slug: str, data: InfoUpdate):
    stmt = select(Info).where(Info.slug == slug).limit(1)
    result = await db.execute(stmt)
    record = result.scalars().first()
    if not record:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)

    return record
