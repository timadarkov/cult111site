from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Info(Base):
    __tablename__ = "info"
    slug: Mapped[str] = mapped_column(primary_key=True)
    info: Mapped[str]
    owners: Mapped[str]
    contacts: Mapped[str]
