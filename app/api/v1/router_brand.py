from fastapi import APIRouter, Depends
from app.dependency import get_current_admin, get_db
from sqlalchemy.orm import Session
from app.services import brand_services
from app.schemas import brand
from app.models.users import User

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


@router.get("", response_model=list[brand.BrandResponse])
def get_brands(db: Session = Depends(get_db)):
    return brand_services.get_brands(db=db)


@router.get("/admin", response_model=list[brand.BrandAdminResponse],)
def get_brands_admin(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return brand_services.get_brands_admin(db=db)


@router.post("/{brand_id}", status_code=204)
def delete_category(
    brand_id: int,
    data: brand.BrandVisibilityUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return brand_services.delete_brand(
        db=db,
        brand_id=brand_id,
        data=data,
    )
