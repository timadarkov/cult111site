from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import brand_services
from app.schemas import brand


router = APIRouter(
    prefix="/brands",
    tags=["Public: Brands"],
)


@router.get("", response_model=list[brand.BrandResponse])
def get_brands(
    db: Session = Depends(get_db),
):
    return brand_services.get_brands(db=db)
