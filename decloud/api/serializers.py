from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'title', 'image', 'url', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == 'processed' and value != 'processed':
            raise serializers.ValidationError("Обработанное изображение нельзя изменить.")
        return value