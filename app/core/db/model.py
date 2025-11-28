import uuid
from sqlalchemy import (
    func,
    Integer,
    DateTime,
    MetaData,
)
from sqlalchemy.types import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declared_attr,
    DeclarativeBase,
)
from app.utils import camel_to_snake
from app.config import base


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    metadata = MetaData(
        naming_convention=base.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_to_snake(cls.__name__)}s"
