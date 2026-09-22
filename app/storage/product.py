from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.category import Category
from app.models.image import Images
from app.models.product import Products
from app.schemas import product
from app.storage import r2


def get_products(db: Session, category_id: int | None = None, brand_id: int | None = None) -> list[Products]:

    query = db.query(Products).options(selectinload(
        Products.images)).filter(Products.is_visible == True)

    if category_id is not None:

        query = query.filter(Products.category_id == category_id)

    if brand_id is not None:

        query = query.filter(Products.brand_id == brand_id)

    return query.all()


def get_product_by_id(db: Session, id: int) -> Products:

    return (db.query(Products).options(selectinload(Products.images)).filter(Products.id == id).filter(Products.is_visible == True).first())


def get_product_by_id_admin(db: Session, product_id: int | None = None) -> list[Products]:

    query = db.query(Products)
    query = query.filter(Products.id == product_id)

    return query.first()


def get_product_admin(db: Session) -> list[Products]:
    query = db.query(Products)
    return query.all()


def create_product(db: Session, data: product.ProductCreate):
    product = Products(
        name=data.name,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        brand_id=data.brand_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product_visibility(
    db: Session,
    product_id: int,
    data: product.ProductVisibilityUpdate,
) -> Products | None:
    product = db.get(Products, product_id)

    if product is None:
        return None

    product.is_visible = data.is_visible

    db.commit()
    db.refresh(product)

    return product


def edit_product(db: Session, product_id: int, data: product.ProductEdit) -> Products | None:
    product = db.get(Products, product_id)

    if product is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def add_product_image(
    db: Session,
    data: product.ProductImageAdd,
    product_id: int,
):
    product = db.get(Products, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not r2.object_exists(data.key):
        raise HTTPException(
            status_code=404,
            detail="Image does not exist in R2"
        )

    image = Images(
        product_id=product_id,
        key=data.key,
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image
