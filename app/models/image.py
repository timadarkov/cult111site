from decimal import Decimal
from sqlalchemy import ForeignKey, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Images(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    key: Mapped[str]
    position: Mapped[int] = mapped_column(default=0, nullable=True)
    is_main: Mapped[bool] = mapped_column(default=False, nullable=True)
    product = relationship(
        "Products",
        back_populates="images"
    )
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
