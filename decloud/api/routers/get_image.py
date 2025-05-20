import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from decloud.api.dependencies import db_dependency
from decloud.api.models import ImageToLoad
from decloud.api.schemas import ErrorCode, ErrorResponse, GetImageResponse

router = APIRouter()


@router.get(
    "/image/get-processed/{task_id}", response_model=GetImageResponse, responses={404: {"model": ErrorResponse}}
)
async def get_image(task_id: uuid.UUID, db: Session = db_dependency) -> GetImageResponse:
    file_instance = db.query(ImageToLoad).filter(ImageToLoad.id == task_id).first()
    if not file_instance:
        raise HTTPException(status_code=404, detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"})

    file_link = file_instance.s3_link if file_instance.status == ImageToLoad.FileProcessing.READY else None
    return GetImageResponse(status=file_instance.status, url=file_link)
