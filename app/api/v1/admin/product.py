from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import image_copy, image_settings, product
from app.services import (
    image_copy_services,
    image_services,
    image_settings_services,
    product_services,
)

router = APIRouter(
    prefix="/products",
    tags=["Admin: Products"],
)


@router.post("", response_model=product.ProductSchemaOut, status_code=201)
async def add_product(
    data: product.ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    return await product_services.add_product(
        db=db,
        data=data,
    )


@router.get("", response_model=list[product.ProductAdminResponse])
async def get_product_admin(db: AsyncSession = Depends(get_db)):
    return await product_services.get_product_admin(db=db)


@router.get("/{product_id}", response_model=product.ProductAdminResponse)
async def get_product_by_id_admin(product_id: int, db: AsyncSession = Depends(get_db)):
    return await product_services.get_product_by_id_admin(db=db, product_id=product_id)


@router.patch("/{product_id}/visibility", response_model=product.ProductAdminResponse, status_code=200)
async def update_product_visibility(
    product_id: int,
    data: product.ProductVisibilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await product_services.update_product_visibility(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.patch("/{product_id}", response_model=product.ProductAdminResponse)
async def edit_product(
    product_id: int,
    data: product.ProductEdit,
    db: AsyncSession = Depends(get_db),
):
    return await product_services.edit_product(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.delete("/{product_id}/images/{image_id}", status_code=204)
async def delete_image(
    product_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    await image_services.delete_image(db, image_id, product_id)


@router.post("/{product_id}/images", response_model=product.ProductImageAdd, status_code=201)
async def add_product_image(
    data: product.ProductImageAdd,
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await image_services.register_image(
        db=db,
        data=data,
        product_id=product_id,
    )


@router.patch("/{product_id}/images/main", status_code=204)
async def update_main_image(
    product_id: int,
    data: image_settings.ImageMainUpdate,
    db: AsyncSession = Depends(get_db),
):
    await image_settings_services.update_main_image(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.patch("/{product_id}/images/order", status_code=204)
async def update_image_order(
    product_id: int,
    data: image_settings.ImageOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    await image_settings_services.update_image_order(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.post("/{product_id}/images/copy", response_model=image_copy.ImageCopyResponse, status_code=201)
async def copy_product_image(
    product_id: int,
    data: image_copy.ImageCopyRequest,
    db: AsyncSession = Depends(get_db),
):
    return await image_copy_services.copy_product_image(
        db=db,
        product_id=product_id,
        data=data,
    )


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    await product_services.delete_product(db, product_id)
