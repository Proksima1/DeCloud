import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from base.presentation.rabbit.rabbit_queues import process_image_queue
from base.settings import settings

logger = logging.getLogger(__name__)


def create_faststream_app() -> tuple[FastStream, RabbitBroker]:
    broker = RabbitBroker(host=settings.rabbit.host, port=settings.rabbit.port)
    app = FastStream(broker)

    @app.on_startup
    async def declare_queues():
        await broker.connect()
        await broker.declare_queue(process_image_queue)

    return app, broker
