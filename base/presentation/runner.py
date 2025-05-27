import asyncio
import logging
from collections.abc import Awaitable
from typing import NoReturn

logger = logging.getLogger(__name__)


async def run(*services: Awaitable[None]) -> NoReturn:
    try:
        tasks = [asyncio.create_task(service) for service in services]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in tasks:
            if not task.done():
                task.cancel()
                continue

            try:
                task.result()
            except Exception:
                logger.exception("exception.in.task")

        logger.info("service.exited", extra={"done": len(done), "pending": len(pending), "total": len(tasks)})

        for service in done:
            if service.exception() is not None:
                logger.error("service.failed", exc_info=service.exception())

    except Exception as e:
        logger.critical("failed.to.start.service", exc_info=e)
