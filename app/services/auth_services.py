from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.utils import encode_jwt, verify_password
from app.storage import users as users_storage


def login(db: Session, username: str, password: str) -> dict[str, str]:
    user = users_storage.get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is blocked",
        )

    token = encode_jwt(payload={"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
