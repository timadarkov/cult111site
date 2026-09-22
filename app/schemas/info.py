
from pydantic import BaseModel


class InfoAdd(BaseModel):
    slug: str
    info: str
    owners: str
    contacts: str


class InfoAdminResponse(BaseModel):
    slug: str
    info: str
    owners: str
    contacts: str
    is_visible: bool


class InfoAdminResponse(BaseModel):
    slug: str
    info: str
    owners: str
    contacts: str
    is_visible: bool


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
    is_visible: bool | None = None
