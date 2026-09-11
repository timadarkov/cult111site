from fastapi import HTTPException
from sqlalchemy.orm import Session
import jwt


from app.auth import utils
from app.core.config import settings
from app.models.users import User
from app.storage import users as users_storage


def login(db: Session, username: str, password: str) -> dict[str, str]:
    user = users_storage.get_user_by_username(db, username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not utils.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is blocked",
        )

    return {
        "access_token": utils.create_token(
            user_id=user.id,
            token_type="access",
            token_expire_minutes=settings.auth_jwt.access_token_expire_minutes
        ),
        "refresh_token": utils.create_token(
            user_id=user.id,
            token_type="refresh",
            token_expire_minutes=settings.auth_jwt.refresh_token_expire_minutes
        ),
        "token_type": "bearer",
    }


def refresh(db: Session, refresh_token: str) -> dict[str, str]:
    try:
        payload = utils.decode_jwt(
            refresh_token,
            expected_type="refresh",
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    user = users_storage.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is blocked",
        )

    return {
        "access_token": utils.create_token(
            user_id=user.id,
            token_type="access",
            token_expire_minutes=settings.auth_jwt.access_token_expire_minutes
        ),
        "refresh_token": utils.create_token(
            user_id=user.id,
            token_type="refresh",
            token_expire_minutes=settings.auth_jwt.refresh_token_expire_minutes
        ),
        "token_type": "bearer",
    }


def get_current_user(db: Session, current_user: int) -> User:
    return users_storage.get_user_by_id(db, current_user.id)
