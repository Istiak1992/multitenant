from rest_framework import serializers
from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    attachment = serializers.FileField(allow_empty_file=False, required=True)

    class Meta:
        model = Photo
        fields = ['id', 'name', 'attachment', 'created', 'updated']
