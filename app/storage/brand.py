from sqlalchemy.orm import Session
from app.schemas.brand import BrandEdit, BrandVisibilityUpdate, BrandAdminResponse, BrandCreate
from app.models.brand import Brands


def get_brands(db: Session) -> list[Brands]:
    return db.query(Brands).filter(Brands.is_visible == True).all()


def get_brands_for_admin(
    db: Session,
    is_visible: bool | None = None,
) -> list[Brands]:

    query = db.query(Brands)

    if is_visible is not None:
        query = query.filter(Brands.is_visible.is_(is_visible))

    return query.all()


def create_brand(db: Session, data: BrandCreate):
    brand = Brands(
        name=data.name,
        is_visible=data.is_visible
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def update_brand_visibility(
    db: Session,
    brand_id: int,
    data: BrandVisibilityUpdate,
) -> Brands | None:
    brand = db.get(Brands, brand_id)

    if brand is None:
        return None

    brand.is_visible = data.is_visible

    db.commit()
    db.refresh(brand)

    return brand


def edit_brand(
    db: Session,
    brand_id: int,
    data: BrandEdit,
) -> Brands | None:
    brand = db.get(Brands, brand_id)

    if brand is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)

    return brand
