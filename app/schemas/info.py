
from pydantic import BaseModel, ConfigDict

class Info(BaseModel):
    info: str
    owners: str
    contacts: str

class imageSchemaOut(BaseModel):
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
    images: list[imageSchemaOut] = []

    
    model_config = ConfigDict(from_attributes=True)

