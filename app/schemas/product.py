from pydantic import BaseModel, ConfigDict

from app.schemas.image import ImageSchemaOut


class ProductSchemaOut(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category_id: int
    brand_id: int
    images: list[ImageSchemaOut] = []

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    category_id: int
    brand_id: int


class ProductAdminResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category_id: int
    brand_id: int
    images: list[ImageSchemaOut] = []
    is_visible: bool

    model_config = ConfigDict(from_attributes=True)


class ProductVisibilityUpdate(BaseModel):
    is_visible: bool


class ProductEdit(BaseModel):
    id: int | None = None
    name: str | None = None
    price: float | None = None
    description: str | None = None
    category_id: int | None = None
    brand_id: int | None = None
    images: list[ImageSchemaOut] = []
    is_visible: bool | None = None


class ProductImageAdd(BaseModel):
    key: str
    position: int = 0
    is_main: bool = False
