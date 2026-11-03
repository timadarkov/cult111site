from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.services import users_services
from app.schemas import user
from app.dependency import get_current_admin
from app.models.users import User

router = APIRouter(
    prefix="/users",
    tags=["Admin: Users"],
)


@router.post("", response_model=user.UserResponse, status_code=201)
def create_users(user: user.UserCreate, db: Session = Depends(get_db),):
    return users_services.create_users(db, user)


@router.get("", response_model=list[user.UserResponseAdmin])
def get_users(
    username: str | None = None,
    email: str | None = None,
    nickname: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    db: Session = Depends(get_db),
):
    return users_services.get_users(
        db=db,
        username=username,
        email=email,
        nickname=nickname,
        is_active=is_active,
        is_verified=is_verified,
    )


@router.patch("/{user_id}/activity", response_model=user.UserResponse, status_code=200)
def update_activity_user(data: user.UserActive, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return users_services.user_deactive(db, user_id, data.is_active, current_user.id)
