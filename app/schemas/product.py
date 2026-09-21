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
