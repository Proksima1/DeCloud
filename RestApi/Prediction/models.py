from django.db import models
from django.utils import timezone

class PhotoTask(models.Model):
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    processed_url = models.URLField(null=True, blank=True)  # URL in S3 after processing
