from core.serializers import BaseSerializer
from rest_framework import serializers

from api.models import ImageToLoad


class StatusResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageToLoad
        fields = ["id", "status"]


class UploadRequestSerializer(BaseSerializer):
    optical_file = serializers.ImageField(allow_empty_file=False)
    sar_file = serializers.ImageField(allow_empty_file=False)


class UploadResponseSerializer(BaseSerializer):
    task_id = serializers.UUIDField()


class GetImageResponseSerializer(BaseSerializer):
    url = serializers.URLField()
    status = serializers.ChoiceField(choices=[(status.value, status.name) for status in ImageToLoad.FileProcessing])


class GetPresignedUrlResponseSerializer(BaseSerializer):
    url = serializers.URLField()
    task_id = serializers.UUIDField()
    expires_date = serializers.DateTimeField()
