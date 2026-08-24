from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Info(Base):
    __tablename__ = "info"
    slug: Mapped[str] = mapped_column(primary_key=True)
    info: Mapped[str]
    owners: Mapped[str]
    contacts: Mapped[str]


class Category(Base):
    __tablename__ = "category"
    id_category: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

