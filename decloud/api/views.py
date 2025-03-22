import uuid
import os
import requests
from datetime import datetime, timedelta

import boto3
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


from api.models import File
from api.serializers import FileSerializer


# Функция создания S3 клиента для Yandex Cloud
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("YC_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("YC_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("YC_ENDPOINT_URL"),
        config=boto3.session.Config(signature_version='s3v4')
    )


class StatusView(APIView):
    permission_classes = []

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
    def get(self, request: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id)
        except File.DoesNotExist:
            return Response({"error": "The task wasn't found!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FileSerializer(file_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PresignedUrlView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        tags=["API бэкенд"],
        operation_description="Генерация Pre-Signed URL для загрузки файла в Yandex S3.",
        responses={
            200: openapi.Response(
                description="Pre-Signed URL и task_id для загрузки файла",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "presigned_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://storage.yandexcloud.net/..."),
                        "task_id": openapi.Schema(
                            type=openapi.TYPE_STRING, example="123e4567-e89b-12d3-a456-426614174000"
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
        },
    )
    def get(self, request):
        task_id = uuid.uuid4()
        bucket_name = os.getenv("YC_STORAGE_BUCKET_NAME")
        cloud_function_url = os.getenv("GENERATE_PRESIGNED_URL")
        if not bucket_name or not cloud_function_url:
            return Response(
                {"error": "Не заданы переменные окружения YC_STORAGE_BUCKET_NAME или GENERATE_PRESIGNED_URL"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        payload = {
            "bucket_name": bucket_name,
            "task_id": str(task_id),
            "expires_in": 3600
        }
        try:
            response = requests.get(cloud_function_url, json=payload, timeout=10)
            response.raise_for_status() 
            data = response.json()
            if "presigned_url" not in data:
                return Response(
                    {"error": "Ответ от сервиса не содержит 'presigned_url'"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            presigned_url = data["presigned_url"]
            File.objects.create(
                id=task_id,
                user=request.user if request.user.is_authenticated else None,
                status="queued",
                s3_link=f"https://storage.yandexcloud.net/{bucket_name}/uploads/{task_id}",
            )
            return Response(
                {"presigned_url": presigned_url, "task_id": str(task_id)},
                status=status.HTTP_200_OK,
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Ошибка при запросе к Yandex Cloud Function: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetImageView(APIView):
    permission_classes = []


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
    def get(self, request: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id, user=request.user if request.user.is_authenticated else None)
        except File.DoesNotExist:
            return Response({"error": "Задача не найдена!"}, status=status.HTTP_404_NOT_FOUND)

        if file_instance.status != "ready":
            return Response({"status": "Файл еще не готов"}, status=status.HTTP_200_OK)

        return Response({"url": file_instance.s3_link}, status=status.HTTP_200_OK)
