from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db, get_current_user
from app.schemas import auth, user
from app.services import auth_services
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=auth.UserLoginResponse)
def login(data: auth.UserLogin, db: Session = Depends(get_db)):
    return auth_services.login(
        db=db,
        username=data.username,
        password=data.password,
    )


@router.post("/refresh", response_model=auth.RefreshResponse)
def refresh(
    data: auth.RefreshRequest,
    db: Session = Depends(get_db),
):
    return auth_services.refresh(
        db=db,
        refresh_token=data.refresh_token,
    )


@router.get("/me", response_model=user.UserResponse)
def me(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return auth_services.get_current_user(
        db=db,
        current_user=current_user,
    )
