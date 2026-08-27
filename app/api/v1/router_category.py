from fastapi import APIRouter


from app.services import categoty_services

router = APIRouter()





@router.get("/category")
def get_categories():
    return categoty_services.get_categories()
