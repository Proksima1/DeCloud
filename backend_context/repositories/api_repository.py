import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend_context.persistent.pg.api import ImageProcess as ImageProcessRecord
from backend_context.persistent.pg.api import ImageProcessing
from backend_context.persistent.pg.api import PresignedUrl as PresignedUrlRecord
from backend_context.schemas.api_schemas import PresignedUrl as PresignedUrlDTO
from backend_context.schemas.api_schemas import Task

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ApiRepository:
    _engine_rw: async_sessionmaker[AsyncSession]
    _engine_ro: async_sessionmaker[AsyncSession]

    async def add_presigned_url(self, url: PresignedUrlDTO) -> bool:
        stmt = (
            insert(PresignedUrlRecord)
            .values(
                url=url.url,
                expires_at=url.expires_date,
            )
            .returning(PresignedUrlRecord.id)
        )
        async with self._engine_rw() as session:
            res = (await session.execute(stmt)).first()
            await session.commit()
        if res is None:
            logger.warning("presigned.url.not.saved", extra={"task_id": url.task_id})
            return False
        return True

    async def add_task(self, task_id: uuid.UUID) -> bool:
        stmt = insert(ImageProcessRecord).values(task_id=task_id).returning(ImageProcessRecord.id)
        async with self._engine_rw() as session:
            res = (await session.execute(stmt)).first()
            await session.commit()
        if res is None:
            logger.warning("task.not.saved", extra={"task_id": task_id})
            return False
        return True

    async def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        stmt = select(ImageProcessRecord).where(ImageProcessRecord.task_id == task_id)
        async with self._engine_ro() as session:
            res = (await session.execute(stmt)).first()
        if res is None:
            return Task(task_id=None, status=ImageProcessing.UNKNOWN, s3_url=None)
        data = res[0]
        return Task(task_id=data.task_id, status=data.status, s3_url=None)
