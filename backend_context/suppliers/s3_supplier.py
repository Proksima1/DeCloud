import json
import uuid
from dataclasses import dataclass

from aiohttp import ClientSession

from backend_context.schemas.api_schemas import PresignedUrl
from base.settings import settings


@dataclass(slots=True, frozen=True, kw_only=True)
class S3Supplier:
    _session: ClientSession

    async def get_presigned_url(self, task_id: uuid.UUID) -> PresignedUrl:
        payload = {"bucket_name": settings.s3_config.bucket_name, "task_id": str(task_id), "expires_in": 3600}
        async with self._session.get(
            settings.s3_config.generate_presigned_url_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()
            data = json.loads(await response.text())
            presigned_url = data.get("presigned_url")
            expiration_datetime = data.get("expiration_time")
            return PresignedUrl(url=presigned_url, task_id=task_id, expires_date=expiration_datetime)
