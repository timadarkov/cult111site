from sqlalchemy.orm import Session
from app.schemas.category import CategoryUpdate
from app.models.category import Category


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).filter(Category.is_visible == True).all()


def create_category(db: Session, data: CategoryUpdate):
    category = Category(
        name=data.name,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = db.get(Category, category_id)

    if category is None:
        return False

    db.delete(category)
    db.commit()

    return True


def update_category(db: Session, category_id: int, data: CategoryUpdate):
    category = db.get(Category, category_id)

    if category is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category
