from fastapi import APIRouter
from app.services import image_services
from app.dependency import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from app.schemas import product

router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


@router.get("", response_model=list[product.ImageSchemaOut])
def get_images(db: Session = Depends(get_db)):
    return image_services.get_images()
