from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic import Field


class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str = Field(min_length=6, max_length=22)
    password: str = Field(min_length=8, max_length=24)
    email: EmailStr | None = None
    nickname: str = Field(min_length=0, max_length=24)


class UserResponse(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: int
    username: str
    email: EmailStr | None = None
    nickname: str


class UserLogin(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str
