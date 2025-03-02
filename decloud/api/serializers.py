from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'user_id', 'status', 's3_link']

    def validate_status(self, value):
        instance = self.instance
        #some needed actions here
        return value