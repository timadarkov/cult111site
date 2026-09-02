from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Images(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    image_url: Mapped[str]

    product: Mapped["Products"] = relationship(
        back_populates="images"
    )


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
    images: Mapped[list["Images"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"

    )
