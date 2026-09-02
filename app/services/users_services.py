from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.auth import UserCreate
from app.auth.utils import hash_password
from app.models.users import User
from app.storage.users import add_user
from app.storage.users import get_users


def create_users(db: Session, user: UserCreate):

    hashed_password = hash_password(user.password)
    user = User(
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        password_hash=hashed_password,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )
    return add_user(db, user)


def get_products(
    db: Session,
    username: str,
    email: str,
    nickname: str,
):
    return get_users(
        db,
        username=username,
        email=email,
        nickname=nickname,
    )
