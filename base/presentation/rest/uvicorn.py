import logging
from typing import NoReturn

import uvicorn
from fastapi import FastAPI

from base.settings import Uvicorn, settings

logger = logging.getLogger(__name__)


async def run(app: FastAPI, config: Uvicorn | None = None) -> NoReturn:  # type: ignore
    if config is None:
        config = settings.uvicorn

    logger.info(
        "uvicorn.service.starting",
        extra={
            "host": config.host,
            "port": config.port,
            "workers": config.workers,
        },
    )

    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=config.host,
            port=config.port,
            workers=config.workers,
            log_config=settings.logger.config(),
        ),
    )
    await server.serve()
