from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import info_services
from app.schemas import info


router = APIRouter(
    prefix="/info",
    tags=["Admin: Info"],
)


@router.post("/admin", response_model=info.InfoAdminResponse, status_code=201)
def add_info(
    data: info.InfoAdd,
    db: Session = Depends(get_db)
):
    return info_services.add_info(
        data=data,
        db=db,
    )


@router.patch("/admin/{slug}", response_model=info.InfoUpdate)
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
