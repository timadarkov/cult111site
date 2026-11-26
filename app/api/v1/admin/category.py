from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import category
from app.services import category_services

router = APIRouter(
    prefix="/categories",
    tags=["Admin: Categories"],
)


@router.get("", response_model=list[category.CategoryAdminResponse])
async def get_categories_admin(db: AsyncSession = Depends(get_db)):
    return await category_services.get_categories_admin(db=db)


@router.post("", response_model=category.CategoryResponse, status_code=201)
async def add_category(
    data: category.CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await category_services.add_category(
        db=db,
        data=data,
    )


@router.patch("/{category_id}", response_model=category.CategoryAdminResponse, status_code=200)
async def edit_category(
    category_id: int,
    data: category.CategoryEdit,
    db: AsyncSession = Depends(get_db),
):
    return await category_services.edit_category(
        db=db,
        category_id=category_id,
        data=data,
    )


@router.patch("/{category_id}/visibility", response_model=category.CategoryAdminResponse, status_code=200)
async def update_category_visibility(
    category_id: int,
    data: category.CategoryVisibilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await category_services.update_category_visibility(
        db=db,
        category_id=category_id,
        data=data,
    )


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    await category_services.delete_category(db, category_id)
