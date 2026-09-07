from fastapi import APIRouter
from app.services import info_services

router = APIRouter(
    prefix="/info",
    tags=["Info"],
)


@router.get("/info")
def get_info():
    return info_services.get_info()
