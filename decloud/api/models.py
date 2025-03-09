import uuid

from django.conf import settings
from django.db import models


class File(models.Model):
    class FileProcessing(models.TextChoices):
        QUEUED = "queued", "Queued"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files")
    status = models.CharField(max_length=20, choices=FileProcessing.choices, default=FileProcessing.QUEUED)
    s3_link = models.URLField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.id} ({self.status})"


class PresignedLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="presigned_links")
    link = models.URLField(max_length=255)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Presigned link for {self.user.username} (expires: {self.expires_at})"
