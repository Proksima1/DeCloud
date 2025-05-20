from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    INTERNAL_ERROR = "internal.error"
    NOT_FOUND = "not.found"
    BAD_REQUEST = "bad.request"


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str


class FileProcessing(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"


class StatusResponse(BaseModel):
    id: UUID
    status: FileProcessing


class UploadRequest(BaseModel):
    optical_file: bytes = Field(..., description="Спутниковый снимок")
    sar_file: bytes = Field(..., description="Радарные данные")


class UploadResponse(BaseModel):
    task_id: UUID


class GetImageResponse(BaseModel):
    url: str | None = None
    status: FileProcessing


class GetPresignedUrlResponse(BaseModel):
    url: str
    task_id: UUID
    expires_date: datetime
