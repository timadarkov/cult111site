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


class Brands(Base):
    __tablename__ = "brands"
    id_brand: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class Products(Base):
    __tablename__ = "products"
    id_product: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[Decimal]
    description: Mapped[str]
    category_id: Mapped[int]
    brand_id: Mapped[int]

class Images(Base):
    __tablename__ = "images"
    id_image: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int]
    image_url: Mapped[str]