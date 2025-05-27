from dataclasses import dataclass

from backend_context.repositories.api_repository import ApiRepository
from backend_context.repositories.s3_repository import S3Repository
from backend_context.services.api_service import ApiService
from backend_context.suppliers.s3_supplier import S3Supplier
from base.containers.base import Container
from base.infrastructure.http.session import new_session_from_settings
from base.infrastructure.pg.client import engine_from_settings_both
from base.infrastructure.rabbit.session import broker_from_settings
from base.infrastructure.s3.session import s3_session_from_settings


@dataclass(slots=True, frozen=True)
class ApiContainer(Container):
    api_service: ApiService

    @classmethod
    async def build_from_settings(cls) -> "ApiContainer":
        http_session = new_session_from_settings()
        s3_supplier = S3Supplier(_session=http_session)

        pg_rw_client, pg_ro_client = engine_from_settings_both()
        api_repository = ApiRepository(pg_rw_client, pg_ro_client)
        s3_session = s3_session_from_settings()
        s3_repository = S3Repository(_s3_session=s3_session)

        rabbit_broker = broker_from_settings()
        await rabbit_broker.connect()
        api_service = ApiService(
            _s3_supplier=s3_supplier,
            _api_repository=api_repository,
            _s3_repository=s3_repository,
            _publisher=rabbit_broker,
        )

        return cls(
            api_service=api_service,
        )
