from fastapi import APIRouter
from app.services import image_services
from app.dependency import get_db, get_current_admin
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.image import ImagePresignRequest, ImageCreate

from app.schemas import product

router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


@router.get("", response_model=list[product.ImageSchemaOut])
def get_images(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return image_services.get_images(
        db=db,
    )


@router.post("/presign")
def presign_image(
    data: ImagePresignRequest,
    admin=Depends(get_current_admin),
):
    return image_services.create_presigned_upload(data)


@router.post("")
def register_image(
    data: ImageCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return image_services.register_image(db, data)


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    image_services.delete_image(db, image_id)
    return {"detail": "Image deleted"}
