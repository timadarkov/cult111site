from fastapi import APIRouter

from app.services import brand_services

router = APIRouter()





@router.get("/brand")
def get_brands():
    return brand_services.get_brands()
