from pydantic import BaseModel


class BrandResponse(BaseModel):
    id: int
    name: str


class BrandAdminResponse(BaseModel):
    id: int
    name: str
    is_visible: bool


class BrandVisibilityUpdate(BaseModel):
    is_visible: bool


class BrandCreate(BaseModel):
    name: str
    is_visible: bool = True


class BrandEdit(BaseModel):
    name: str | None = None
    is_visible: bool | None = None
