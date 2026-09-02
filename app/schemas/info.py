
from pydantic import BaseModel


class Info(BaseModel):
    info: str
    owners: str
    contacts: str
