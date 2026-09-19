import jwt
import bcrypt
from app.core.config import settings
from datetime import datetime, timedelta, timezone

PUBLIC_KEY = settings.auth_jwt.public_key_path.read_text()
PRIVATE_KEY = settings.auth_jwt.private_key_path.read_text()


def encode_jwt(
        payload: dict,
        private_key: str = PRIVATE_KEY,
        algorithm: str = settings.auth_jwt.algorithm,
):

    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        token: str | bytes,
        expected_type: str,
        public_key: str = PUBLIC_KEY,
        algorithm: str = settings.auth_jwt.algorithm,
):
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        options={"require": ["sub", "exp", "type"]},
    )

    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")

    return payload


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(
        password: str,
        hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password.encode(),
    )


def create_token(user_id: int | str, token_type: str, token_expire_minutes: int) -> str:
    return encode_jwt(
        payload={
            "sub": str(user_id),
            "type": token_type,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=token_expire_minutes),
            "iat": datetime.now(timezone.utc),
        }
    )
