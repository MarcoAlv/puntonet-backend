import enum
from app.core.db.model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum, Boolean, Index
from sqlalchemy.orm import relationship


class User(Base):
    class BaseUserRole(enum.Enum):
        ADMIN = "admin"
        STAFF = "staff"
        MANAGER = "manager"
        CUSTOMER = "customer"
        PROVIDER = "provider"

    full_name : Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[BaseUserRole] = mapped_column(
        Enum(BaseUserRole), default=BaseUserRole.CUSTOMER, nullable=False)

    store_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None
    )

    __table_args__ = (
        Index(
            "uq_store_name_not_null",
            "store_name",
            unique=True,
            postgresql_where=(store_name.isnot(None)),
        ),
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sells: Mapped[list["Sell"]] = relationship(
        "Sell",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
