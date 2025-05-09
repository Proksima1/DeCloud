import datetime
import uuid

from backend_context.persistent.pg.api import ImageProcessing
from base.schemas.base import PureBaseModel


class PresignedUrl(PureBaseModel):
    url: str
    task_id: uuid.UUID
    expires_date: datetime.datetime


class Task(PureBaseModel):
    task_id: uuid.UUID | None
    status: ImageProcessing
    s3_url: str | None
