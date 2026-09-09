from fastapi import APIRouter

from app.services import brand_services
from app.schemas import brand


router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


@router.get("", response_model=list[brand.BrandResponse])
def get_brands():
    return brand_services.get_brands()
