
from pydantic import BaseModel


class InfoResponse(BaseModel):
    slug: str
    info: str
    owners: str
    contacts: str


class InfoUpdate(BaseModel):
    slug: str | None = None
    info: str | None = None
    owners: str | None = None
    contacts: str | None = None
