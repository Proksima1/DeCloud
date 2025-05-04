import datetime
import uuid

from backend_context.persistent.pg.api import ImageProcessing
from base.schemas.base import CamelizedBaseModel


class PresignedUrl(CamelizedBaseModel):
    url: str
    task_id: uuid.UUID
    expires_date: datetime.datetime


class Task(CamelizedBaseModel):
    task_id: uuid.UUID | None
    status: ImageProcessing
    s3_url: str | None
