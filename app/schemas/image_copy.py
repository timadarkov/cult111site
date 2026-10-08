from pydantic import BaseModel, ConfigDict, Field

from app.schemas.image import ImageSchemaOut


class ImageCopyRequest(BaseModel):
    image_id: int = Field(gt=0, strict=True)


class ImageCopyResponse(ImageSchemaOut):
    model_config = ConfigDict(from_attributes=True)
