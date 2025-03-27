import uuid
from datetime import datetime, timedelta

from api.models import File
from api.serializers import (
    GetImageResponseSerializer,
    GetPresignedUrlResponseSerializer,
    StatusResponseSerializer,
    UploadRequestSerializer,
    UploadResponseSerializer,
)
from core.serializers import ErrorResponseSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class MockUploadView(APIView):
    @extend_schema(
        request=UploadRequestSerializer,
        responses={201: UploadResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Mock"],
    )
    def post(self, request: Request) -> Response:
        serializer = UploadRequestSerializer.create_and_validate(data=request.data, files=request.FILES)

        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED,
        )


class MockStatusView(APIView):
    @extend_schema(responses={200: StatusResponseSerializer, 404: ErrorResponseSerializer}, tags=["Mock"])
    def get(self, _: Request, task_id: str) -> Response:
        file_instance = File(
            id=task_id,
            user=None,
            status=File.FileProcessing.PROCESSING,
            s3_link=f"https://link.rur/image/{uuid.uuid4()}",
        )
        serializer = StatusResponseSerializer(file_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MockPresignedUrlView(APIView):
    @extend_schema(responses={200: GetPresignedUrlResponseSerializer, 500: ErrorResponseSerializer}, tags=["Mock"])
    def get(self, _request: Request) -> Response:
        task_id = uuid.uuid4()
        serializer = GetPresignedUrlResponseSerializer.create_and_validate(
            url=f"https://mock-storage.example.com/upload/{task_id}",
            task_id=task_id,
            expires_date=(datetime.now() + timedelta(hours=1)).isoformat(),
        )
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class MockGetImageView(APIView):
    @extend_schema(responses={200: GetImageResponseSerializer, 404: ErrorResponseSerializer}, tags=["Mock"])
    def get(self, _request: Request, task_id: str) -> Response:
        serializer = GetImageResponseSerializer.create_and_validate(
            status=File.FileProcessing.READY, url=f"https://hello.me/asfasf/{task_id}"
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
