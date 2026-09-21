from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CERTS_DIR = BASE_DIR / "certs"


class AuthJWT(BaseModel):

    private_key_path: Path = CERTS_DIR / "private.pem"
    public_key_path: Path = CERTS_DIR / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 7*24*60


class Settings(BaseSettings):

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    host_url: list[str]
    r2_endpoint: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket: str
    r2_public_url: str
    image_max_size: int

    auth_jwt: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
