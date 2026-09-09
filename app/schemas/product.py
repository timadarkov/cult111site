from pydantic import BaseModel, ConfigDict


class ImageSchemaOut(BaseModel):
    id: int
    product_id: int
    image_url: str

    model_config = ConfigDict(from_attributes=True)


class ProductSchemaOut(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category_id: int
    brand_id: int
    images: list[ImageSchemaOut] = []

    model_config = ConfigDict(from_attributes=True)
