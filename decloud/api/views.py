import uuid

import requests
from core.serializers import ErrorCode, ErrorResponseSerializer
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import File
from api.serializers import (
    GetImageResponseSerializer,
    GetPresignedUrlResponseSerializer,
    StatusResponseSerializer,
    UploadRequestSerializer,
    UploadResponseSerializer,
)


class UploadView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=UploadRequestSerializer,
        responses={201: UploadResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Prod"],
    )
    def post(self, request: Request) -> Response:
        if "file" not in request.FILES:
            serializer = ErrorResponseSerializer.create_and_validate(
                code=ErrorCode.BAD_REQUEST, message="There is no file in request"
            )
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = UploadRequestSerializer.create_and_validate(data=request.data, files=request.FILES)

        uploaded_file = serializer.validated_data.get("file")
        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"

        # s3 = get_s3_client()
        # s3.upload_fileobj(uploaded_file, settings.YC_STORAGE_BUCKET_NAME, file_name)
        # TODO: загрузка в s3

        file_instance = File(
            id=uuid.uuid4(),
            user=request.user if request.user.is_authenticated else None,
            status=File.FileProcessing.QUEUED,
            s3_link=f"https://storage.yandexcloud.net/{settings.YC_STORAGE_BUCKET_NAME}/{file_name}",
        )
        file_instance.save()
        serializer = UploadResponseSerializer.create_and_validate(task_id=file_instance.id)
        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED,
        )


class StatusView(APIView):
    permission_classes = []

    @extend_schema(responses={200: StatusResponseSerializer, 404: ErrorResponseSerializer}, tags=["Prod"])
    def get(self, _: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id)
        except File.DoesNotExist:
            serializer = ErrorResponseSerializer.create_and_validate(code=ErrorCode.NOT_FOUND, message="Task not found")
            return Response(serializer.validated_data, status=status.HTTP_404_NOT_FOUND)

        serializer = StatusResponseSerializer(file_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PresignedUrlView(APIView):
    permission_classes = []

    @extend_schema(responses={200: GetPresignedUrlResponseSerializer, 500: ErrorResponseSerializer}, tags=["Prod"])
    def get(self, request: Request) -> Response:
        task_id = uuid.uuid4()
        payload = {"bucket_name": settings.YC_STORAGE_BUCKET_NAME, "task_id": str(task_id), "expires_in": 3600}
        try:
            response = requests.get(settings.YC_GENERATE_PRESIGNED_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "presigned_url" not in data:
                serializer = ErrorResponseSerializer.create_and_validate(
                    code=ErrorCode.INTERNAL_ERROR, message="YC unexpected response"
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            presigned_url = data.get("presigned_url")
            expiration_datetime = data.get("expiration_time")
            File.objects.create(
                id=task_id,
                user=request.user if request.user.is_authenticated else None,
                status=File.FileProcessing.QUEUED,
                s3_link=f"https://storage.yandexcloud.net/{settings.YC_STORAGE_BUCKET_NAME}/uploads/{task_id}",
            )
            serializer = GetPresignedUrlResponseSerializer.create_and_validate(
                url=presigned_url, task_id=task_id, expires_date=expiration_datetime
            )
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK,
            )
        except requests.exceptions.RequestException:
            serializer = ErrorResponseSerializer.create_and_validate(
                code=ErrorCode.INTERNAL_ERROR, message="YC request error"
            )
            return Response(
                serializer.data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetImageView(APIView):
    permission_classes = []

    @extend_schema(responses={200: GetImageResponseSerializer, 404: ErrorResponseSerializer}, tags=["Prod"])
    def get(self, _: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id)
        except File.DoesNotExist:
            serializer = ErrorResponseSerializer(code=ErrorCode.NOT_FOUND, message="YC unexpected response")
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        file_link = file_instance.s3_link if file_instance.status == File.FileProcessing.READY else None
        serializer = GetImageResponseSerializer.create_and_validate(status=file_instance.status, url=file_link)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
