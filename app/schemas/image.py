from pydantic import BaseModel, ConfigDict, computed_field

from app.core.config import Settings


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

    @computed_field
    @property
    def url(self) -> str:
        return f"{Settings.r2_public_url.rstrip('/')}/{self.key}"
