
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User


def add_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    return user


async def get_users(db: AsyncSession, username: str | None = None, email: str | None = None, nickname: str | None = None, is_active: bool | None = None, is_verified: bool | None = None,
                    ) -> list[User]:
    stmt = select(User)

    if username:
        stmt = stmt.where(User.username == username)
    if email:
        stmt = stmt.where(User.email == email)
    if nickname:
        stmt = stmt.where(User.nickname == nickname)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if is_verified is not None:
        stmt = stmt.where(User.is_verified == is_verified)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, id: int) -> User | None:
    return await db.get(User, id)


async def user_deactive(
    db: AsyncSession,
    user_id: int,
    is_active: bool,
) -> User | None:

    user = await db.get(User, user_id)

    if not user:
        return None

    user.is_active = is_active

    await db.commit()
    await db.refresh(user)

    return user
