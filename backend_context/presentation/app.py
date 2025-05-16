import logging
import uuid

from fastapi import APIRouter, FastAPI, File, UploadFile

# from neuro_api_context.settings import settings
from backend_context.containers.api_container import ApiContainer
from backend_context.schemas.api_schemas import PresignedUrl, Task
from base.presentation.rest.app import create_fastapi_app

logger = logging.getLogger(__name__)


async def create_app(container: ApiContainer) -> FastAPI:
    router = APIRouter(prefix="/v1", tags=["Prod"])
    mock_router = APIRouter(prefix="/mock", tags=["Mock"])

    @router.post("/image/upload")
    async def upload_image(
        optical_file: UploadFile = File(..., description="Спутниковый снимок"),
        sar_file: UploadFile = File(..., description="Радарный снимок"),
    ) -> Task:
        return await container.api_service.upload_satellite_images(optical_file=optical_file, sar_file=sar_file)

    @router.get("/image/{task_id}")
    async def get_image(task_id: uuid.UUID) -> Task:
        return await container.api_service.get_image_by_task_id(task_id=task_id)

    @router.get("/get-presigned-url")
    async def get_presigned_url() -> PresignedUrl:
        return await container.api_service.get_presigned_url()

    app = create_fastapi_app()
    app.include_router(router)
    router.include_router(mock_router)

    return app
