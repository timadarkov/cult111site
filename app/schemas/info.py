
from pydantic import BaseModel


class InfoResponse(BaseModel):
    slug: str
    info: str
    owners: str
    contacts: str
