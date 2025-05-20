import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy.orm import Session

from decloud.api.dependencies import db_dependency, file_dependency
from decloud.api.models import ImageToLoad
from decloud.api.schemas import ErrorCode, ErrorResponse, UploadResponse

router = APIRouter()


@router.post("/image/upload/", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = file_dependency, db: Session = db_dependency) -> UploadResponse:
    if not file:
        raise HTTPException(
            status_code=400, detail={"code": ErrorCode.BAD_REQUEST, "message": "There is no file in request"}
        )

    file_instance = ImageToLoad(id=uuid.uuid4(), status=ImageToLoad.FileProcessing.PENDING, s3_link=None)
    db.add(file_instance)
    db.commit()
    db.refresh(file_instance)

    return UploadResponse(task_id=file_instance.id)
