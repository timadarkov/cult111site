from app.services import users_services
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependency import get_db
from app.schemas import user
from app.dependency import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=user.UserResponse, status_code=201)
def creare_users(user: user.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return users_services.create_users(db, user)


@router.get("", response_model=list[user.UserResponse])
def get_users(
    username: str | None = None,
    email: str | None = None,
    nickname: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return users_services.get_users(
        db=db,
        username=username,
        email=email,
        nickname=nickname,
        is_active=is_active,
        is_verified=is_verified,
    )
