from pydantic import BaseModel, ConfigDict


class ImagePresignRequest(BaseModel):
    content_type: str


class ImagePresignResponse(BaseModel):
    upload_url: str
    key: str


class ImageCreate(BaseModel):
    key: str


class ImageSchemaOut(BaseModel):
    id: int
    product_id: int
    key: str

    model_config = ConfigDict(from_attributes=True)
