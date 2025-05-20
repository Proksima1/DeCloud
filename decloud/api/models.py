import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileProcessing(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"


class ImageToLoad(Base):
    __tablename__ = "image_to_load"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(SQLAlchemyEnum(FileProcessing), default=FileProcessing.QUEUED)
    created_at = Column(DateTime, default=datetime.utcnow)
    s3_link = Column(String, nullable=True)

    def __str__(self):
        return f"File {self.id} ({self.status})"


class PresignedLink(Base):
    __tablename__ = "presigned_link"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    link = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __str__(self):
        return f"Presigned link for user {self.user_id} (expires: {self.expires_at})"
