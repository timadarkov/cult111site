from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str
    email: EmailStr | None = None
    nickname: str
    is_active: bool = True
    is_verified: bool = False


class UserResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str
    email: EmailStr | None = None
    nickname: str


class UserLogin(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str
