import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from neuro_api_context.settings import settings

logger = logging.getLogger(__name__)


def create_faststream_app() -> RabbitBroker:
    broker = RabbitBroker(host=settings.rabbit.host, port=settings.rabbit.port)
    app = FastStream(broker)

    return broker
