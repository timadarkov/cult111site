from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Category(Base):
    __tablename__ = "category"
    id_category: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
