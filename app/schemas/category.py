from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoryUpdate(BaseModel):
    name: str


class CategoryCreate(BaseModel):
    name: str
    is_visible: bool = True
