import logging
import uuid

from faststream import FastStream

from base.presentation.rabbit.rabbit_queues import process_image_queue
from neuro_api_context.containers.neuro_api_container import NeuroApiContainer
from neuro_api_context.presentation.app import create_faststream_app

logger = logging.getLogger(__name__)


async def create_app(container: NeuroApiContainer) -> FastStream:
    # router = RabbitRouter(prefix="decloud_")
    app, broker = create_faststream_app()

    @broker.subscriber(process_image_queue)
    async def process_images(task_id: uuid.UUID) -> None:
        try:
            await container.neuro_api_service.process_task(task_id)
            logger.info("imaged.processed", extra={"task_id": task_id})
        except Exception as e:
            logger.exception("processing.image.error.occurred", extra={"task_id": task_id}, exc_info=e)
            raise

    # broker.include_router(router)
    return app
