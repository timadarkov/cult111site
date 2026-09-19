from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, true
from database import Base


class Brands(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
