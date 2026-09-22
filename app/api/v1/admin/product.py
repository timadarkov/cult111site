from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import product_services
from app.schemas import product


router = APIRouter(
    prefix="/products",
    tags=["Admin: Products"],
)


@router.post("/{product_id}/images", response_model=product.ProductImageAdd, status_code=201)
def add_product_image(
    data: product.ProductImageAdd,
    product_id: int,
    db: Session = Depends(get_db)
):
    return product_services.add_product_image(
        db=db,
        data=data,
        product_id=product_id,
    )


@router.post("", response_model=product.ProductSchemaOut, status_code=201)
def add_product(
    data: product.ProductCreate,
    db: Session = Depends(get_db)
):
    return product_services.add_product(
        db=db,
        data=data,
    )


@router.get("", response_model=list[product.ProductAdminResponse])
def get_product_admin(db: Session = Depends(get_db)):
    return product_services.get_product_admin(db=db)


@router.get("/{product_id}", response_model=product.ProductAdminResponse)
def get_product_by_id_admin(product_id: int, db: Session = Depends(get_db)):
    return product_services.get_product_by_id_admin(db=db, product_id=product_id)


@router.patch("/visibility/{product_id}", status_code=200)
def update_product_visibility(
    product_id: int,
    data: product.ProductVisibilityUpdate,
    db: Session = Depends(get_db),
):
    return product_services.update_product_visibility(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.patch("/{product_id}")
def edit_product(
    product_id: int,
    data: product.ProductEdit,
    db: Session = Depends(get_db),
):
    return product_services.edit_product(
        db=db,
        product_id=product_id,
        data=data,
    )
