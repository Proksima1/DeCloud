import uuid

from sqlalchemy import Column, DateTime, MetaData  # type: ignore
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase

from base.utils.datetime_utils import utcnow


class Base(DeclarativeBase):
    meta = MetaData(schema="public")


class WithId:
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4(),
        primary_key=True,
        comment="Идентификатор записи",
    )


class WithCreatedAt:
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), default=utcnow(), nullable=False, comment="Дата создания записи")


class WithUpdatedAt:
    __abstract__ = True

    updated_at = Column(
        DateTime(timezone=True),
        default=utcnow(),
        onupdate=utcnow(),
        nullable=False,
        comment="Дата обновления записи",
    )
