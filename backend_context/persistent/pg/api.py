import enum

from sqlalchemy import UUID, BigInteger, Column, DateTime, Enum, Text

from base.persistent.pg.base import Base, WithCreatedAt, WithUpdatedAt
from base.utils.datetime_utils import utcnow


class ImageProcessing(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    UNKNOWN = "unknown"


class ImageProcess(Base, WithCreatedAt, WithUpdatedAt):
    __tablename__ = "image_process"

    id = Column(BigInteger, primary_key=True)
    task_id = Column(UUID(as_uuid=True), index=True)
    status = Column(Enum(ImageProcessing), nullable=False, default=ImageProcessing.QUEUED)


class PresignedUrl(Base, WithCreatedAt, WithUpdatedAt):
    __tablename__ = "presigned_url"

    id = Column(UUID(as_uuid=True), primary_key=True)
    url = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), default=utcnow())
