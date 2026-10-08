from typing import Annotated

from pydantic import BaseModel, Field


class ImageMainUpdate(BaseModel):
    image_id: int = Field(gt=0, strict=True)


class ImageOrderUpdate(BaseModel):
    image_ids: list[Annotated[int, Field(gt=0, strict=True)]] = Field(min_length=1)
