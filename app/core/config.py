from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CERTS_DIR = BASE_DIR / "certs"


class AuthJWT(BaseModel):

    private_key_path: Path = CERTS_DIR / "private.pem"
    public_key_path: Path = CERTS_DIR / "public.pem"
    algorithm: str = "RS256"


class Settings(BaseSettings):
    Database_url: str
    host_url: list[str]

    auth_jwt: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
