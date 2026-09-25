from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import image_services, product_services
from app.schemas import product


router = APIRouter(
    prefix="/products",
    tags=["Admin: Products"],
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


@router.patch("/{product_id}/visibility", response_model=product.ProductAdminResponse, status_code=200)
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


@router.patch("/{product_id}", response_model=product.ProductAdminResponse)
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


@router.delete("/products/{product_id}/images/{image_id}", status_code=204)
def delete_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
):
    image_services.delete_image(db, image_id, product_id)


@router.post("/{product_id}/images", response_model=product.ProductImageAdd, status_code=201)
def add_product_image(
    data: product.ProductImageAdd,
    product_id: int,
    db: Session = Depends(get_db)
):
    return image_services.register_image(
        db=db,
        data=data,
        product_id=product_id,
    )
