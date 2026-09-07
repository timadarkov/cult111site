from app.services import users_services
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependency import get_db
from app.schemas.auth import UserCreate


router = APIRouter()


@router.post("/users")
def creare_users(user: UserCreate, db: Session = Depends(get_db)):
    return users_services.create_users(db, user)


@router.get("/users")
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
