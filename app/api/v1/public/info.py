from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import info_services
from app.schemas import info


router = APIRouter(
    prefix="/info",
    tags=["Public: Info"],
)


@router.get("", response_model=list[info.InfoResponse])
def get_info(db: Session = Depends(get_db)):
    return info_services.get_info(db=db)
