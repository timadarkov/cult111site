from fastapi import APIRouter


from app.services import categoty_services
from app.schemas import category

router = APIRouter(
    prefix="/catefories",
    tags=["Catefories"],
)


@router.get("", response_model=list[category.CategoryResponse])
def get_categories():
    return categoty_services.get_categories()
