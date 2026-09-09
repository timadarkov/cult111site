from fastapi import APIRouter
from app.schemas.product import ProductSchemaOut
from app.services import product_services, image_services
from app.dependency import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/{product_id}", response_model=ProductSchemaOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_services.get_product_by_id(db, product_id)


@router.get("", response_model=list[ProductSchemaOut])
def get_products(
    category_id: int | None = None,
    brand_id: int | None = None,
    db: Session = Depends(get_db)
):
    return product_services.get_products(
        category_id=category_id,
        brand_id=brand_id,
        db=db,
    )
