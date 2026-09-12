from sqlalchemy.orm import Session
from app.schemas.brand import BrandVisibilityUpdate, BrandAdminResponse
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


def delete_brand(
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
