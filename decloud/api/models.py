from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import uuid

class File(models.Model):

    STATUS_CHOICES = [
        'queued',
        'processing',
        'ready'
    ]

    id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )
    s3_link = models.URLField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title