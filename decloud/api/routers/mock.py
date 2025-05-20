import asyncio
import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy.orm import Session

from decloud.api.dependencies import db_dependency, file_dependency
from decloud.api.models import ImageToLoad
from decloud.api.schemas import (
    ErrorCode,
    ErrorResponse,
    GetImageResponse,
    GetPresignedUrlResponse,
    GetStatusResponse,
    UploadResponse,
)

router = APIRouter()


@router.post("/mock/image/upload/", response_model=UploadResponse)
async def mock_upload_file(file: UploadFile = file_dependency, db: Session = db_dependency) -> UploadResponse:
    # Используем file для валидации, но не обрабатываем его в моке
    _ = file
    file_instance = ImageToLoad(id=uuid.uuid4(), status=ImageToLoad.FileProcessing.PENDING, s3_link=None)
    db.add(file_instance)
    db.commit()
    db.refresh(file_instance)
    return UploadResponse(task_id=file_instance.id)


@router.get("/mock/image/status/{task_id}", response_model=GetStatusResponse, responses={404: {"model": ErrorResponse}})
async def mock_get_status(task_id: uuid.UUID, db: Session = db_dependency) -> GetStatusResponse:
    file_instance = db.query(ImageToLoad).filter(ImageToLoad.id == task_id).first()
    if not file_instance:
        raise HTTPException(status_code=404, detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"})

    if file_instance.status == ImageToLoad.FileProcessing.PENDING:
        await asyncio.sleep(2)
        file_instance.status = ImageToLoad.FileProcessing.READY
        file_instance.s3_link = "https://example.com/mock-image.jpg"
        db.commit()

    return GetStatusResponse(status=file_instance.status)


@router.get(
    "/mock/image/get-processed/{task_id}", response_model=GetImageResponse, responses={404: {"model": ErrorResponse}}
)
async def mock_get_image(task_id: uuid.UUID, db: Session = db_dependency) -> GetImageResponse:
    file_instance = db.query(ImageToLoad).filter(ImageToLoad.id == task_id).first()
    if not file_instance:
        raise HTTPException(status_code=404, detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"})

    file_link = file_instance.s3_link if file_instance.status == ImageToLoad.FileProcessing.READY else None
    return GetImageResponse(status=file_instance.status, url=file_link)


@router.get("/mock/get-presigned-url/", response_model=GetPresignedUrlResponse)
async def mock_get_presigned_url() -> GetPresignedUrlResponse:
    return GetPresignedUrlResponse(
        url="https://example.com/upload",
        fields={
            "key": "mock-file.jpg",
            "bucket": "mock-bucket",
            "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
            "X-Amz-Credential": "mock-credential",
            "X-Amz-Date": "20240101T000000Z",
            "Policy": "mock-policy",
            "X-Amz-Signature": "mock-signature",
        },
    )
