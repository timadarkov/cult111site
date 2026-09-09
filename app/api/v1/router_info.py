from fastapi import APIRouter
from app.services import info_services
from app.schemas import info

router = APIRouter(
    prefix="/info",
    tags=["Info"],
)


@router.get("", response_model=info.InfoResponse)
def get_info():
    return info_services.get_info()
