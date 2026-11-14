from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.dependency import get_current_user, get_db
from app.models.users import User
from app.schemas import auth, user
from app.services import auth_services

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/login", response_model=auth.UserLoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: auth.UserLogin,
    db: Session = Depends(get_db),
):
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
def me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return auth_services.get_current_user(
        db=db,
        current_user=current_user,
    )
