from faststream.rabbit import RabbitBroker

from base.settings import settings


def broker_from_settings() -> RabbitBroker:
    return RabbitBroker(
        host=settings.rabbit.host,
        port=settings.rabbit.port,
    )
