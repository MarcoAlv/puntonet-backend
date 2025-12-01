from decimal import Decimal
from datetime import datetime
from app.core.db.model import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, String, Enum, Boolean, ForeignKey, Integer, DateTime
from app.models.users import User


class Product(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    free_shipping: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    description: Mapped[str] = mapped_column(String(800), nullable=False)
    specs: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="products"
    )

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan"
    )


class ProductImage(Base):

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False
    )

    path: Mapped[str] = mapped_column(String(300), nullable=False)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product = relationship(
        "Product",
        back_populates="images"
    )


class Review(Base):
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(600), nullable=False)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )

    product = relationship(
        "Product",
        back_populates="reviews"
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )


class DetailSell(Base):
    sell_id: Mapped[int] = mapped_column(
        ForeignKey("sell.id"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )

    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    price_unit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    product = relationship("Product")


class Sell(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    paid: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="sells"
    )

    details = relationship(
        "DetailSell",
        backref="sell",
        cascade="all, delete-orphan"
    )


class Favorite(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )

    user = relationship(
        "User",
        back_populates="favorites"
    )

    product = relationship("Product")


class Cart(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, unique=True
    )

    user = relationship(
        "User",
        back_populates="cart"
    )

    items = relationship(
        "CartItem",
        backref="cart",
        cascade="all, delete-orphan"
    )


class CartItem(Base):
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("cart.id"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )

    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product = relationship("Product")
