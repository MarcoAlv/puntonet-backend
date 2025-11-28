import enum
from app.core.db.model import Base
from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    class BaseUserRole(enum.Enum):
        ADMIN = "admin"
        STAFF = "staff"
        MANAGER = "manager"
        CUSTOMER = "customer"
        PROVIDER = "provider"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[BaseUserRole] = mapped_column(
        Enum(BaseUserRole), default=BaseUserRole.CUSTOMER, nullable=False)
