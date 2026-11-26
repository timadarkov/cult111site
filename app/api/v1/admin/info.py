from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import info
from app.services import info_services

router = APIRouter(
    prefix="/info",
    tags=["Admin: Info"],
)


@router.post("", response_model=info.InfoAdminResponse, status_code=201)
async def add_info(
    data: info.InfoAdd,
    db: AsyncSession = Depends(get_db)
):
    return await info_services.add_info(
        data=data,
        db=db,
    )


@router.patch("/{slug}", response_model=info.InfoUpdate)
async def update_info(
    slug: str,
    data: info.InfoUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await info_services.update_info(
        slug=slug,
        data=data,
        db=db,
    )
