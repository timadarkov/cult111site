from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import product_services
from app.schemas import product


router = APIRouter(
    prefix="/products",
    tags=["Public: Products"],
)


@router.get("/{product_id}", response_model=product.ProductSchemaOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_services.get_product_by_id(db, product_id)


@router.get("", response_model=list[product.ProductSchemaOut])
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
