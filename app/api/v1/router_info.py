from fastapi import APIRouter
from app.models.users import User
from app.services import info_services
from app.schemas import info
from app.dependency import get_current_admin, get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(
    prefix="/info",
    tags=["Info"],
)


@router.get("", response_model=info.InfoResponse)
def get_info():
    return info_services.get_info()


@router.patch("/update", response_model=info.InfoResponse)
def update_info(
    info: info.InfoUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return info_services.update_info(
        info,
        current_admin,
        db=db,
    )
