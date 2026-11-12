from sqlalchemy import Boolean, true
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
