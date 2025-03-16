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
from rest_framework.permissions import IsAuthenticated


from api.models import File
from api.serializers import FileSerializer


# Функция создания S3 клиента для Yandex Cloud
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("YC_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("YC_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("YC_ENDPOINT_URL"),
    )


class UploadView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        tags=["API бэкенд"],
        operation_description="Загрузка файлов и генерация Pre-Signed URL для загрузки в Yandex S3.",
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
                                        type=openapi.TYPE_STRING, example="https://storage.yandexcloud.net/..."
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
    def post(self, request) -> Response:
        if "file" not in request.FILES:
            return Response({"error": "There is no file in request"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES["file"]
        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        bucket_name = os.getenv("YC_STORAGE_BUCKET_NAME")

        file_instance = File(
            id=uuid.uuid4(),
            user=request.user,
            status="queued",
            s3_link=f"https://storage.yandexcloud.net/{bucket_name}/{file_name}",
        )
        file_instance.save()

        s3 = get_s3_client()
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_name,
            },
            ExpiresIn=3600,
        )

        return Response(
            {
                "task_ids": [
                    {
                        "task_id": str(file_instance.id),
                        "presigned_url": presigned_url,
                        "expire-date": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d"),
                    }
                ]
            },
            status=status.HTTP_201_CREATED,
        )


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
    def get(self, request: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id)
        except File.DoesNotExist:
            return Response({"error": "The task wasn't found!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FileSerializer(file_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PresignedUrlView(APIView):
    permission_classes = [IsAuthenticated]

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
        cloud_function_url = os.getenv("GENERATE_PESIGNED_URL")
        payload = {
            "bucket_name": bucket_name,
            "task_id": str(task_id),
        }
        response = requests.get(cloud_function_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            presigned_url = data["presigned_url"]
            File.objects.create(
                id=task_id,
                user=request.user,
                status="queued",
                s3_link=f"https://storage.yandexcloud.net/{bucket_name}/uploads/{task_id}",
            )

            return Response(
                {"presigned_url": presigned_url, "task_id": str(task_id)},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Ошибка при генерации Pre-Signed URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
    def get(self, request: Request, task_id: uuid.UUID) -> Response:
        try:
            file_instance = File.objects.get(id=task_id, user=request.user)
        except File.DoesNotExist:
            return Response({"error": "Задача не найдена!"}, status=status.HTTP_404_NOT_FOUND)

        if file_instance.status != "ready":
            return Response({"status": "Файл еще не готов"}, status=status.HTTP_200_OK)

        return Response({"url": file_instance.s3_link}, status=status.HTTP_200_OK)
