from fastapi import APIRouter
from app.schemas.info import ProductSchemaOut
from app.services import product_services, image_services


router = APIRouter()




@router.get("/product", response_model=list[ProductSchemaOut])
def get_products():
    return product_services.get_products()

@router.get("/product/{product_id}", response_model=ProductSchemaOut)
def get_product_by_id(product_id: int):
    return product_services.get_product_by_id(product_id)

@router.get("/product/category/{category_id}", response_model=list[ProductSchemaOut])
def get_products_by_category(category_id: int):
    return product_services.get_products_by_category(category_id)

@router.get("/product/brand/{brand_id}", response_model=list[ProductSchemaOut])
def get_products_by_brand(brand_id: int):
    return product_services.get_products_by_brand(brand_id)

@router.get("/image")
def get_images():
    return image_services.get_images()