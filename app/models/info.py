from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, true
from database import Base


class Info(Base):
    __tablename__ = "info"
    slug: Mapped[str] = mapped_column(primary_key=True)
    info: Mapped[str]
    owners: Mapped[str]
    contacts: Mapped[str]
    is_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true())
