from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import brand_services
from app.schemas import brand


router = APIRouter(
    prefix="/brands",
    tags=["Admin: Brands"],
)


@router.get("", response_model=list[brand.BrandAdminResponse])
def get_brands_admin(
    db: Session = Depends(get_db),
):
    return brand_services.get_brands_admin(db=db)


@router.post("", response_model=brand.BrandResponse, status_code=201)
def add_brand(
    data: brand.BrandCreate,
    db: Session = Depends(get_db),
):
    return brand_services.add_brand(
        db=db,
        data=data,
    )


@router.patch("/{brand_id}", response_model=list[brand.BrandAdminResponse], status_code=200)
def edit_brand(
    brand_id: int,
    data: brand.BrandEdit,
    db: Session = Depends(get_db),
):
    return brand_services.edit_brand(
        db=db,
        brand_id=brand_id,
        data=data,
    )


@router.patch("/{brand_id}/visibility", response_model=list[brand.BrandAdminResponse], status_code=200)
def update_brand_visibility(
    brand_id: int,
    data: brand.BrandVisibilityUpdate,
    db: Session = Depends(get_db),
):
    return brand_services.update_brand_visibility(
        db=db,
        brand_id=brand_id,
        data=data,
    )
