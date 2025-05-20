import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from decloud.api.dependencies import db_dependency
from decloud.api.models import ImageToLoad
from decloud.api.schemas import ErrorCode, ErrorResponse, GetStatusResponse

router = APIRouter()


@router.get("/image/status/{task_id}", response_model=GetStatusResponse, responses={404: {"model": ErrorResponse}})
async def get_status(task_id: uuid.UUID, db: Session = db_dependency) -> GetStatusResponse:
    file_instance = db.query(ImageToLoad).filter(ImageToLoad.id == task_id).first()
    if not file_instance:
        raise HTTPException(status_code=404, detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"})

    return GetStatusResponse(status=file_instance.status)
