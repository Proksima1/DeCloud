import uuid
import os
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from models import File
from serializers import FileSerializer


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

    def post(self, request) -> Response:
        if "file" not in request.FILES:
            return Response({"error": "There is no file in request"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES["file"]

        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_name)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        
        file_instance = File(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(), 
            status="queued",
            s3_link=f"/media/uploads/{file_name}", #atm files will be in the folder, according to the plan
        )
        file_instance.save()

        serializer = FileSerializer(file_instance)

        return Response(
            {
                "task_ids": [    #just an example
                    {
                        "task_id": str(file_instance.id),
                        "presigned_url": f"http://localhost:8000{file_instance.s3_link}", # :D
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
            return Response(
                {"error": "The task wasn't found!"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = FileSerializer(file_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)



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

    def get(self, request: Request, task_id: uuid.UUID) -> Response:
        #try:    #This isa possible logic for get-url function
        #    file_instance = File.objects.get(id=task_id)
        #except File.DoesNotExist:
        #    return Response(
        #        {"error": "The task wasn't found!"}, status=status.HTTP_404_NOT_FOUND
        #    )
        #serializer = FileSerializer(file_instance)
        #if serializer.data["status"] != 'ready':
        #    return Response({"not ready yet": "The task is not ready yet!"}, status=status.HTTP_200_OK)
        #return Response(serializer.data["s3_link"], status=status.HTTP_200_OK)

        return Response({"answer": 
                         "https://elements-resized.envatousercontent.com/elements-video-cover-images/files/e6161b21-521b-4968-a41e-1274b484c6cd/inline_image_preview.jpg?w=500&cf_fit=cover&q=85&format=auto&s=926245cddbce52e66bb1e714a69d291b23fab9ec19424fba7486f084f5781332"},
                           status=status.HTTP_200_OK) #mock function

