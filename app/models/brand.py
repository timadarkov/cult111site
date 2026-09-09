from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Brands(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
