from decimal import Decimal
from sqlalchemy import ForeignKey, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.image import Images
from database import Base


class Products(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[Decimal]
    description: Mapped[str]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id_category", ondelete="CASCADE")
    )

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id_brand", ondelete="CASCADE")
    )
    images = relationship(
        "Images",
        back_populates="product",
        cascade="all, delete-orphan"

    )
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
