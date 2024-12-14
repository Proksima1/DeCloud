from rest_framework import serializers
from .models import PhotoTask

class PhotoTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTask
        fields = '__all__'
