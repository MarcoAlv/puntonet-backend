from typing import Type, TypeVar, Generic, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from datetime import datetime
import uuid
import logging

from app.core.db.model import Base

T = TypeVar("T", bound="Base")
IDType = int
UUIDType = uuid.UUID


class BaseCRUD(Generic[T]):
    model: Type[T] = None  # set in subclass

    def __init__(cls, model: Type[T]):
        cls.model = model

    @classmethod
    async def create(cls, db: AsyncSession, obj: T) -> T:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        item_id: IDType,
        include_deleted: bool = False,
    ) -> Optional[T]:
        stmt = select(
            cls.model
        ).where(
            cls.model.id == item_id,
        )
        if not include_deleted:
            stmt = stmt.where(cls.model.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_uuid(
        cls,
        db: AsyncSession,
        item_uuid: UUIDType,
        include_deleted: bool = False,
    ) -> Optional[T]:
        stmt = select(
            cls.model
        ).where(
            cls.model.uuid == item_uuid,
        )
        if not include_deleted:
            stmt = stmt.where(cls.model.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls, db: AsyncSession,
        skip: int | None = None,
        limit: int | None = None,
        include_deleted: bool = False
    ) -> List[T]:
        stmt = select(cls.model)
        if not include_deleted:
            stmt = stmt.where(cls.model.deleted_at.is_(None))
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def count(cls, db: AsyncSession, include_deleted: bool = False) -> int:
        stmt = select(func.count(cls.model.id))
        if not include_deleted:
            stmt = stmt.where(cls.model.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar() or 0
