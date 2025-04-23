from core.serializers import BaseSerializer
from rest_framework import serializers

from api.models import File


class StatusResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "status"]


class UploadRequestSerializer(BaseSerializer):
    file = serializers.ImageField(allow_empty_file=False)


class UploadResponseSerializer(BaseSerializer):
    task_id = serializers.UUIDField()


class GetImageResponseSerializer(BaseSerializer):
    url = serializers.URLField()
    status = serializers.ChoiceField(choices=[(status.value, status.name) for status in File.FileProcessing])


class GetPresignedUrlResponseSerializer(BaseSerializer):
    url = serializers.URLField()
    task_id = serializers.UUIDField()
    expires_date = serializers.DateTimeField()
