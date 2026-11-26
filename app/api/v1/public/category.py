from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import category
from app.services import category_services

router = APIRouter(
    prefix="/categories",
    tags=["Public: Categories"],
)


@router.get("", response_model=list[category.CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await category_services.get_categories(db=db)
