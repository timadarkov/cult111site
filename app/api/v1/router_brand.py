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


@router.get(
    "/admin",
    response_model=list[brand.BrandAdminResponse],
    dependencies=[Depends(get_current_admin)],
)
def get_brands_admin(db: Session = Depends(get_db),):
    return brand_services.get_brands_admin(db=db)


@router.post("", response_model=brand.BrandResponse, dependencies=[Depends(get_current_admin)], status_code=201)
def add_brand(
    data: brand.BrandCreate,
    db: Session = Depends(get_db)
):
    return brand_services.add_brand(
        db=db,
        data=data,
    )


@router.patch("/{brand_id}", status_code=200, dependencies=[Depends(get_current_admin)])
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


@router.patch("/delete/{brand_id}", status_code=200, dependencies=[Depends(get_current_admin)])
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
