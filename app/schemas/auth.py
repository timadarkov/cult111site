from pydantic import BaseModel, ConfigDict


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str
