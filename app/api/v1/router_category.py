from fastapi import APIRouter


from app.services import category_services
from app.schemas import category
from app.dependency import get_current_admin, get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("", response_model=list[category.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_services.get_categories(db=db)


@router.get("/admin", response_model=list[category.CategoryAdminResponse], dependencies=[Depends(get_current_admin)])
def get_categories_admin(db: Session = Depends(get_db),):
    return category_services.get_categories_admin(db=db)


@router.post("", response_model=category.CategoryResponse, dependencies=[Depends(get_current_admin)], status_code=201)
def add_category(
    data: category.CategoryCreate,
    db: Session = Depends(get_db)
):
    return category_services.add_category(
        db=db,
        data=data,
    )


@router.patch("/{category_id}", dependencies=[Depends(get_current_admin)])
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


@router.patch("/delete/{category_id}", status_code=200, dependencies=[Depends(get_current_admin)])
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
