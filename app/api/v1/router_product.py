from fastapi import APIRouter
from app.schemas.info import ProductSchemaOut
from app.services import product_services, image_services


router = APIRouter()


@router.get("/product/{product_id}", response_model=ProductSchemaOut)
def get_product(product_id: int):
    return product_services.get_product_by_id(product_id)


@router.get("/products", response_model=list[ProductSchemaOut])
def get_products(
    category_id: int | None = None,
    brand_id: int | None = None,
):
    return product_services.get_products(
        category_id=category_id,
        brand_id=brand_id,
    )


@router.get("/image")
def get_images():
    return image_services.get_images()
