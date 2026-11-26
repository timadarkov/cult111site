from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import brand
from app.services import brand_services

router = APIRouter(
    prefix="/brands",
    tags=["Admin: Brands"],
)


@router.get("", response_model=list[brand.BrandAdminResponse])
async def get_brands_admin(
    db: AsyncSession = Depends(get_db),
):
    return await brand_services.get_brands_admin(db=db)


@router.post("", response_model=brand.BrandResponse, status_code=201)
async def add_brand(
    data: brand.BrandCreate,
    db: AsyncSession = Depends(get_db),
):
    return await brand_services.add_brand(
        db=db,
        data=data,
    )


@router.patch("/{brand_id}", response_model=brand.BrandAdminResponse, status_code=200)
async def edit_brand(
    brand_id: int,
    data: brand.BrandEdit,
    db: AsyncSession = Depends(get_db),
):
    return await brand_services.edit_brand(
        brand_id=brand_id,
        data=data,
        db=db,
    )


@router.patch("/{brand_id}/visibility", response_model=brand.BrandAdminResponse, status_code=200)
async def update_brand_visibility(
    brand_id: int,
    data: brand.BrandVisibilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await brand_services.update_brand_visibility(
        db=db,
        brand_id=brand_id,
        data=data,
    )


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
):
    await brand_services.delete_brand(db, brand_id)
