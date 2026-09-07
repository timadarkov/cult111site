from fastapi import APIRouter
from app.services import image_services
from app.dependency import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


@router.get("/image")
def get_images(db: Session = Depends(get_db)):
    return image_services.get_images()
