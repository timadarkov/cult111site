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
    payload = payload.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth_jwt.access_token_expire_minutes
    )

    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = PUBLIC_KEY,
        algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


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
