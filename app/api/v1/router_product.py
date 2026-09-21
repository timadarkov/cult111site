from fastapi import APIRouter
from app.schemas import product
from app.services import product_services, image_services
from app.dependency import get_current_admin, get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/admin/{product_id}/images", response_model=product.ProductImageAdd, dependencies=[Depends(get_current_admin)], status_code=201)
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


@router.post("/admin", response_model=product.ProductSchemaOut, dependencies=[Depends(get_current_admin)], status_code=201)
def add_product(
    data: product.ProductCreate,
    db: Session = Depends(get_db)
):
    return product_services.add_product(
        db=db,
        data=data,
    )


@router.get("/admin", response_model=list[product.ProductAdminResponse], dependencies=[Depends(get_current_admin)])
def get_product_admin(db: Session = Depends(get_db)):
    return product_services.get_product_admin(db=db)


@router.get("/admin/{product_id}", response_model=product.ProductAdminResponse, dependencies=[Depends(get_current_admin)])
def get_product_by_id_admin(product_id: int, db: Session = Depends(get_db)):
    return product_services.get_product_by_id_admin(db=db, product_id=product_id)


@router.patch("/admin/visibility/{product_id}", status_code=200, dependencies=[Depends(get_current_admin)])
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


@router.patch("/admin/{product_id}", dependencies=[Depends(get_current_admin)])
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
