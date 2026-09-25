from sqlalchemy.orm import Session
from app.schemas import category
from app.models.category import Category


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).filter(Category.is_visible == True).all()


def create_category(db: Session, data: category.CategoryCreate):
    category = Category(
        name=data.name,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category_visibility(
    db: Session,
    category_id: int,
    data: category.CategoryVisibilityUpdate,
) -> Category | None:
    category = db.get(Category, category_id)

    if not category:
        return None

    category.is_visible = data.is_visible

    db.commit()
    db.refresh(category)

    return category


def get_category_for_admin(
    db: Session,
    is_visible: bool | None = None,
) -> list[Category]:

    query = db.query(Category)

    if is_visible is not None:
        query = query.filter(Category.is_visible.is_(is_visible))

    return query.all()


def edit_category(db: Session, category_id: int, data: category.CategoryEdit) -> Category | None:
    category = db.get(Category, category_id)

    if not category:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category
