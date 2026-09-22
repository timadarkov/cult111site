from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import category_services
from app.schemas import category


router = APIRouter(
    prefix="/categories",
    tags=["Admin: Categories"],
)


@router.get("", response_model=list[category.CategoryAdminResponse])
def get_categories_admin(db: Session = Depends(get_db),):
    return category_services.get_categories_admin(db=db)


@router.post("", response_model=category.CategoryResponse, status_code=201)
def add_category(
    data: category.CategoryCreate,
    db: Session = Depends(get_db)
):
    return category_services.add_category(
        db=db,
        data=data,
    )


@router.patch("/{category_id}")
def edit_category(
    category_id: int,
    data: category.CategoryEdit,
    db: Session = Depends(get_db),
):
    return category_services.edit_category(
        db=db,
        category_id=category_id,
        data=data,
    )


@router.patch("/visibility/{category_id}", status_code=200)
def update_category_visibility(
    category_id: int,
    data: category.CategoryVisibilityUpdate,
    db: Session = Depends(get_db),
):
    return category_services.update_category_visibility(
        db=db,
        category_id=category_id,
        data=data,
    )
