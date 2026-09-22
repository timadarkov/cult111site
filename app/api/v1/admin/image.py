from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import image_services
from app.schemas import image, product


router = APIRouter(
    prefix="/images",
    tags=["Admin: Images"],
)


@router.get("", response_model=list[product.ImageSchemaOut])
def get_images(db: Session = Depends(get_db)):
    return image_services.get_images(
        db=db,
    )


@router.post("/presign", response_model=image.ImagePresignResponse)
def presign_image(
    data: image.ImagePresignRequest,
):
    return image_services.create_presigned_upload(data)
