from fastapi import APIRouter


from app.services import categoty_services

router = APIRouter(
    prefix="/catefories",
    tags=["Catefories"],
)


@router.get("/categories")
def get_categories():
    return categoty_services.get_categories()
