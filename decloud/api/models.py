from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Image(models.Model):

    STATUS_CHOICES = [
        'uploaded',
        'processing',
        'processed'
    ]

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    url = models.URLField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )

    def __str__(self):
        return self.title