from fastapi import APIRouter
from app.schemas.info import Info
from app.services import home_services

router = APIRouter()


@router.get("/main")
def get_info():
    return home_services.get_info()

@router.get("/category")
def get_categories():
    return home_services.get_categories()