from sqlalchemy.orm import Session
from app.schemas import user
from app.auth.utils import hash_password
from app.models.users import User
from app.storage import users as users_storage
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def create_users(db: Session, user: user.UserCreate):

    hashed_password = hash_password(user.password)
    user = User(
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        password_hash=hashed_password,
    )
    try:
        db_user = users_storage.add_user(db, user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )


def get_users(
    db: Session,
    username: str,
    email: str,
    nickname: str,
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    return users_storage.get_users(
        db,
        username=username,
        email=email,
        nickname=nickname,
        is_active=is_active,
        is_verified=is_verified,
    )


def get_user_by_username(db: Session, username: str):
    return users_storage.get_user_by_username(db, username)


def user_deactive(
    db: Session,
    user_id: int,
    is_active: bool,
    current_user_id: int,
) -> User:
    if current_user_id == user_id and not is_active:
        raise HTTPException(
            status_code=403,
            detail="You cannot deactivate yourself",
        )

    user = users_storage.user_deactive(db, user_id, is_active)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
