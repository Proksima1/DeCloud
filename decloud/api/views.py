import uuid

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class UploadView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        tags=["API бэкенд"],
        operation_description="Загрузка файлов и генерация Pre-Signed URL для загрузки в S3.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "file": openapi.Schema(type=openapi.TYPE_FILE, description="Файл для загрузки"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Pre-Signed URL и task_id для загрузки файла",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "task_ids": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "task_id": openapi.Schema(
                                        type=openapi.TYPE_STRING, example="123e4567-e89b-12d3-a456-426614174000"
                                    ),
                                    "presigned_url": openapi.Schema(
                                        type=openapi.TYPE_STRING, example="https://s3.amazonaws.com/..."
                                    ),
                                    "expire-date": openapi.Schema(type=openapi.TYPE_STRING, example="2020-02-01"),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
        },
    )
    def post(self, _: Request) -> Response:
        return Response({"response": "hello"})


class StatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["API бэкенд"],
        operation_description="Получение статуса задачи по task_id.",
        responses={
            200: openapi.Response(
                description="Статус задачи",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "task_id": openapi.Schema(
                            type=openapi.TYPE_STRING, example="123e4567-e89b-12d3-a456-426614174000"
                        ),
                        "filename": openapi.Schema(type=openapi.TYPE_STRING, example="photo.jpg"),
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="pending"),
                    },
                ),
            ),
            404: openapi.Response(description="Задача не найдена"),
        },
    )
    def get(self, _: Request, task_id: uuid.UUID) -> Response:
        return Response({"response": task_id})


class PresignedUrlView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["API бэкенд"],
        operation_description="Генерация Pre-Signed URL для загрузки файла в S3.",
        responses={
            200: openapi.Response(
                description="Pre-Signed URL и task_id для загрузки файла",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "presigned_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://s3/..."),
                        "task_id": openapi.Schema(
                            type=openapi.TYPE_STRING, example="123e4567-e89b-12d3-a456-426614174000"
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
        },
    )
    def post(self, _: Request) -> Response:
        return Response({"response": "hello"})


class GetImageView(APIView):
    @swagger_auto_schema(
        operation_description="Получить обработанное изображение по task_id",
        manual_parameters=[
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Уникальный идентификатор задачи (UUID)",
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="Обработанное изображение в формате файла",
                ),
            ),
            404: openapi.Response(
                description="Задача не найдена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                        )
                    },
                ),
            ),
        },
        tags=["API бэкенд"],
    )
    def get(self, _: Request, task_id: uuid.UUID) -> Response:
        return Response({"response": task_id})
