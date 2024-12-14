import boto3
from sys import exit
from readers import readS3Keys
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
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
    permission_classes = [permissions.IsAuthenticated] #Add Authentication

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
    permission_classes = [permissions.IsAuthenticated] #Add Authentication

    def get(self, request, task_id, format=None):
        try:
            task = PhotoTask.objects.get(task_id=task_id)
            serializer = PhotoTaskSerializer(task)
            return Response(serializer.data)
        except PhotoTask.DoesNotExist:
            return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class PresignedUrlView(APIView):
    permission_classes = [permissions.AllowAny] #No Authentication needed for presigned url

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
                Params={'Bucket': BUCKET_NAME, 'Key': task_id, 'ContentType': 'image/jpeg'}, #Adjust content type
                ExpiresIn=3600
            )
            return Response({'presigned_url': presigned_url, 'task_id': task_id}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'detail': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


   
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
    def get(self, request, format=None):
        sum = 0
        # Add the numbers
        data = request.data
        for key in data:
            sum += data[key]
        response_dict = {"sum": sum}
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
