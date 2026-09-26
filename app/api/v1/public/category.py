from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import category_services
from app.schemas import category


router = APIRouter(
    prefix="/categories",
    tags=["Public: Categories"],
)


@router.get("", response_model=list[category.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_services.get_categories(db=db)
