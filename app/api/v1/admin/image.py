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


@router.post("/presign")
def presign_image(
    data: image.ImagePresignRequest,
):
    return image_services.create_presigned_upload(data)


@router.post("",)
def register_image(
    data: image.ImageCreate,
    db: Session = Depends(get_db),
):
    return image_services.register_image(db, data)


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
):
    image_services.delete_image(db, image_id)
    return {"detail": "Image deleted"}
