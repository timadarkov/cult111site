from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas import category


async def get_categories(db: AsyncSession) -> list[Category]:
    stmt = select(Category).where(Category.is_visible.is_(True))
    result = await db.execute(stmt)
    return result.scalars().all()


def create_category(db: AsyncSession, data: category.CategoryCreate):
    category = Category(
        name=data.name,
        is_visible=data.is_visible,
    )
    db.add(category)
    return category


async def update_category_visibility(
    db: AsyncSession,
    category_id: int,
    data: category.CategoryVisibilityUpdate,
) -> Category | None:
    category = await db.get(Category, category_id)

    if not category:
        return None

    category.is_visible = data.is_visible

    await db.commit()
    await db.refresh(category)

    return category


async def get_category_for_admin(
    db: AsyncSession,
    is_visible: bool | None = None,
) -> list[Category]:

    query = select(Category)

    if is_visible is not None:
        query = query.where(Category.is_visible.is_(is_visible))

    result = await db.execute(query)
    return list(result.scalars().all())


async def edit_category(db: AsyncSession, category_id: int, data: category.CategoryEdit) -> Category | None:
    category = await db.get(Category, category_id)

    if not category:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return category


async def delete_category(db: AsyncSession, category_id: int):
    category = await db.get(Category, category_id)

    if category is None:
        return None

    await db.delete(category)
    await db.commit()

    return category
