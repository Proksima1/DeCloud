import logging

from faststream import FastStream
from faststream.rabbit import RabbitRouter

from neuro_api_context.containers.neuro_api_container import NeuroApiContainer
from neuro_api_context.presentation.app import create_faststream_app

logger = logging.getLogger(__name__)


async def create_app(container: NeuroApiContainer) -> FastStream:
    router = RabbitRouter(prefix="decloud_")

    @router.subscriber("process_images")
    async def process_images(event: ...) -> None: ...

    broker = create_faststream_app()
    broker.include_router(router)
    return broker
