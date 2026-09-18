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
