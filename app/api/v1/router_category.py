from fastapi import APIRouter


from app.services import category_services
from app.schemas import category
from app.dependency import get_current_admin, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.users import User

router = APIRouter(
    prefix="/catefories",
    tags=["Catefories"],
)


@router.get("", response_model=list[category.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_services.get_categories(db=db)


@router.post("/add", response_model=category.CategoryResponse, status_code=201)
def add_category(
    data: category.CategoryCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return category_services.add_category(
        data=data,
        db=db,
    )


@router.patch("/{category_id}")
def update_category(
    category_id: int,
    data: category.CategoryUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return category_services.update_category(
        db=db,
        category_id=category_id,
        data=data,
    )
