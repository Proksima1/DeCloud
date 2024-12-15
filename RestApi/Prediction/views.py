import boto3
from sys import exit
from readers import readS3Keys
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import PhotoTask
from .serializers import PhotoTaskSerializer
from rest_framework import permissions
import json
import uuid


keys = readS3Keys("key.txt")
if keys == None:
    exit("Wrong format of the key file!")

s3 = boto3.client('s3', aws_access_key_id=keys["key_id"], aws_secret_access_key=keys["key"], region_name=keys["region"])
BUCKET_NAME = keys["bucket_name"]


class UploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Загрузка файлов и генерация Pre-Signed URL для загрузки в S3.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE, description="Файл для загрузки"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Pre-Signed URL и task_id для загрузки файла",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_ids': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'task_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                              example="123e4567-e89b-12d3-a456-426614174000"),
                                    'presigned_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    example="https://s3.amazonaws.com/..."),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
        },
    )
    def post(self, request, format=None):
        files = request.FILES
        task_ids = []
        for filename, file in files.items():
            task_id = str(uuid.uuid4())
            task = PhotoTask(filename=filename, task_id=task_id)
            task.save()

            presigned_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': BUCKET_NAME, 'Key': task_id, 'ContentType': file.content_type},
                ExpiresIn=3600
            )

            task_ids.append({'task_id': task_id, 'presigned_url': presigned_url})
        return Response({'task_ids': task_ids}, status=status.HTTP_201_CREATED)


class StatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение статуса задачи по task_id.",
        responses={
            200: openapi.Response(
                description="Статус задачи",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING, example="123e4567-e89b-12d3-a456-426614174000"),
                        'filename': openapi.Schema(type=openapi.TYPE_STRING, example="photo.jpg"),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="pending"),
                    },
                ),
            ),
            404: openapi.Response(description="Задача не найдена"),
        },
    )
    def get(self, request, task_id, format=None):
        try:
            task = PhotoTask.objects.get(task_id=task_id)
            serializer = PhotoTaskSerializer(task)
            return Response(serializer.data)
        except PhotoTask.DoesNotExist:
            return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class PresignedUrlView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Генерация Pre-Signed URL для загрузки файла в S3.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'filename': openapi.Schema(type=openapi.TYPE_STRING, description="Имя файла"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Pre-Signed URL и task_id для загрузки файла",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'presigned_url': openapi.Schema(type=openapi.TYPE_STRING,
                                                        example="https://s3/..."),
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                  example="123e4567-e89b-12d3-a456-426614174000"),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
            500: openapi.Response(description="Внутренняя ошибка сервера"),
        },
    )
    def post(self, request, format=None):
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            if not filename:
                return Response({'detail': 'Filename is required'}, status=status.HTTP_400_BAD_REQUEST)

            task_id = str(uuid.uuid4())
            task = PhotoTask(filename=filename, task_id=task_id)
            task.save()

            presigned_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': BUCKET_NAME, 'Key': task_id, 'ContentType': 'image/jpeg'},
                ExpiresIn=3600
            )
            return Response({'presigned_url': presigned_url, 'task_id': task_id}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'detail': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


   
@swagger_auto_schema(
    method='get',
    operation_description="Этот эндпоинт ничего не делает. Он просто возвращает пустой ответ.",
    responses={
        200: openapi.Response(description="Пустой ответ"),
    },
)
@swagger_auto_schema(
    method='post',
    operation_description="Суммирует числа, переданные в теле запроса.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'num1': openapi.Schema(type=openapi.TYPE_INTEGER, description="Первое число"),
            'num2': openapi.Schema(type=openapi.TYPE_INTEGER, description="Второе число"),
        },
    ),
    responses={
        201: openapi.Response(
            description="Сумма чисел",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'sum': openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
                },
            ),
        ),
        400: openapi.Response(description="Ошибка в запросе"),
    },
)
@api_view(['GET', 'POST'])
def api_add(request):
    sum = 0
    response_dict = {}
    if request.method == 'GET':
        # Do nothing
        pass
    elif request.method == 'POST':
        # Add the numbers
        data = request.data
        for key in data:
            sum += data[key]
        response_dict = {"sum": sum}
    return Response(response_dict, status=status.HTTP_201_CREATED)


class Add_Values(APIView):
    @swagger_auto_schema(
        operation_description="Суммирует числа, переданные в теле запроса.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'num1': openapi.Schema(type=openapi.TYPE_INTEGER, description="Первое число"),
                'num2': openapi.Schema(type=openapi.TYPE_INTEGER, description="Второе число"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Сумма чисел",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'sum': openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
                    },
                ),
            ),
            400: openapi.Response(description="Ошибка в запросе"),
        },
    )
    def post(self, request, format=None):
        sum = 0
        # Add the numbers
        data = request.data
        for key in data:
            sum += data[key]
        response_dict = {"sum": sum}
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
