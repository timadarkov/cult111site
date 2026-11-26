from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import brand
from app.services import brand_services

router = APIRouter(
    prefix="/brands",
    tags=["Public: Brands"],
)


@router.get("", response_model=list[brand.BrandResponse])
async def get_brands(
    db: AsyncSession = Depends(get_db),
):
    return await brand_services.get_brands(db=db)
