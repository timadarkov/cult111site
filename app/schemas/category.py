from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoryEdit(BaseModel):
    name: str | None = None
    is_visible: bool | None = None


class CategoryCreate(BaseModel):
    name: str
    is_visible: bool = True


class CategoryAdminResponse(BaseModel):
    id: int
    name: str
    is_visible: bool


class CategoryVisibilityUpdate(BaseModel):
    is_visible: bool
