from fastapi import APIRouter
from app.services import info_services, categoty_services, brand_services, product_services, image_services


router = APIRouter()


@router.get("/main")
def get_info():
    return info_services.get_info()

@router.get("/category")
def get_categories():
    return categoty_services.get_categories()

@router.get("/brand")
def get_brands():
    return brand_services.get_brands()

@router.get("/product")
def get_products():
    return product_services.get_products()

@router.get("/image")
def get_images():
    return image_services.get_images()