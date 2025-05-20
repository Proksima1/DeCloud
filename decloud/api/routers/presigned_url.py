import uuid

import aiohttp
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from decloud.api.config import settings
from decloud.api.dependencies import db_dependency
from decloud.api.models import ImageToLoad
from decloud.api.schemas import ErrorCode, ErrorResponse, GetPresignedUrlResponse

router = APIRouter()


@router.get("/get-presigned-url/", response_model=GetPresignedUrlResponse, responses={500: {"model": ErrorResponse}})
async def get_presigned_url(db: Session = db_dependency) -> GetPresignedUrlResponse:
    task_id = uuid.uuid4()
    payload = {"bucket_name": settings.YC_STORAGE_BUCKET_NAME, "task_id": str(task_id), "expires_in": 3600}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.YC_GENERATE_PRESIGNED_URL, json=payload, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                if "presigned_url" not in data:
                    raise HTTPException(
                        status_code=500, detail={"code": ErrorCode.INTERNAL_ERROR, "message": "YC unexpected response"}
                    )

                presigned_url = data.get("presigned_url")
                expiration_datetime = data.get("expiration_time")

                file_instance = ImageToLoad(
                    id=task_id,
                    user_id=None,  # TODO: добавить авторизацию
                    status=ImageToLoad.FileProcessing.QUEUED,
                    s3_link=f"https://storage.yandexcloud.net/{settings.YC_STORAGE_BUCKET_NAME}/uploads/{task_id}",
                )
                db.add(file_instance)
                db.commit()
                db.refresh(file_instance)

                return GetPresignedUrlResponse(url=presigned_url, task_id=task_id, expires_date=expiration_datetime)
    except aiohttp.ClientError as err:
        raise HTTPException(
            status_code=500, detail={"code": ErrorCode.INTERNAL_ERROR, "message": "YC request error"}
        ) from err
