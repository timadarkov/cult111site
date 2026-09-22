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


@router.get("", response_model=list[info.InfoResponse])
def get_info(db: Session = Depends(get_db)):
    return info_services.get_info(db=db)


@router.post("/admin", response_model=info.InfoAdminResponse, dependencies=[Depends(get_current_admin)], status_code=201)
def add_info(
    data: info.InfoAdd,
    db: Session = Depends(get_db)
):
    return info_services.add_info(
        data=data,
        db=db,
    )


@router.patch("/admin/{slug}", response_model=info.InfoUpdate, dependencies=[Depends(get_current_admin)])
def update_info(
    slug: str,
    data: info.InfoUpdate,
    db: Session = Depends(get_db)
):
    return info_services.update_info(
        slug=slug,
        data=data,
        db=db,
    )
