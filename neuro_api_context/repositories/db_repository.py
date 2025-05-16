import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend_context.persistent.pg.api import ImageProcess as ImageProcessRecord
from backend_context.persistent.pg.api import ImageProcessing

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class DBRepository:
    _engine_rw: async_sessionmaker[AsyncSession]
    _engine_ro: async_sessionmaker[AsyncSession]

    async def update_task_status(self, task_id: uuid.UUID, new_status: ImageProcessing) -> bool:
        stmt = (
            update(ImageProcessRecord)
            .where(ImageProcessRecord.task_id == task_id)
            .values(status=new_status)
            .returning(ImageProcessRecord.id)
        )

        async with self._engine_rw() as session:
            res = (await session.execute(stmt)).first()
            await session.commit()
        if res is None:
            logger.warning("task.status.not.updated", extra={"task_id": task_id})
            return False
        return True
