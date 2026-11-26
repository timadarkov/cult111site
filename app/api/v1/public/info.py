from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import info
from app.services import info_services

router = APIRouter(
    prefix="/info",
    tags=["Public: Info"],
)


@router.get("", response_model=list[info.InfoResponse])
async def get_info(db: AsyncSession = Depends(get_db)):
    return await info_services.get_info(db=db)
