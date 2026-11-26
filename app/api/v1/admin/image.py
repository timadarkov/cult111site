from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.schemas import image, product
from app.services import image_services

router = APIRouter(
    prefix="/images",
    tags=["Admin: Images"],
)


@router.get("", response_model=list[product.ImageSchemaOut])
async def get_images(db: AsyncSession = Depends(get_db)):
    return await image_services.get_images(db=db)


@router.post("/presign", response_model=image.ImagePresignResponse)
def presign_image(
    data: image.ImagePresignRequest,
):
    return image_services.create_presigned_upload(data=data)
