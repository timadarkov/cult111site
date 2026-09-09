from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.schemas import auth
from app.services import auth_services

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=auth.UserLoginResponse)
def login(data: auth.UserLogin, db: Session = Depends(get_db)):
    return auth_services.login(
        db=db,
        username=data.username,
        password=data.password,
    )
