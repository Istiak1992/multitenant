# from abc import ABC
from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.fields import (
    CharField,
    ListField,
    IntegerField,
    EmailField,
    FileField
)
from photo.serializers import PhotoSerializer
from photo.models import Photo


class UserSerializer(serializers.Serializer):
    id = IntegerField(required=True)
    username = CharField(required=True)
    name = CharField(required=True, allow_null=True, allow_blank=True)
    email = EmailField(required=True)
    address = CharField(allow_blank=True, allow_null=True)
    language_preferences = CharField(required=True)
    permissions = ListField()

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['id', 'full_name', 'last_name', 'email', 'language_preferences']


class UserProfileSerializer(serializers.Serializer):
    id = IntegerField(required=True)
    username = CharField(required=True)
    name = CharField(required=True, allow_null=True, allow_blank=True, source='first_name')
    email = EmailField(required=True)
    address = CharField(allow_blank=True, allow_null=True)
    language_preferences = CharField(required=True)
    photo = PhotoSerializer()
    # permissions = ListField()

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['id', 'name', 'email', 'language_preferences', 'photo']
        depth = 2


class UserProfileUpdateSerializer(serializers.Serializer):
    id = IntegerField(required=True)
    username = CharField(required=True)
    name = CharField(required=True, allow_null=True, allow_blank=True, source='first_name')
    email = EmailField(required=True)
    address = CharField(allow_blank=True, allow_null=True)
    photo = PhotoSerializer(many=False, allow_null=True)
    language_preferences = CharField(required=True)
    profile_photo = FileField(required=True, allow_null=True, write_only=True)

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['id', 'name', 'email', 'language_preferences', 'photo']
        depth = 2

    def update(self, instance, validated_data):
        profile_photo = validated_data.get('profile_photo')
        photo_data = None

        if profile_photo is not None:
            photo_serializer = PhotoSerializer(data={'name': 'profile_photo', 'attachment': profile_photo})

            if photo_serializer.is_valid():
                photo_serializer.save()
                photo_data = photo_serializer.data
                photo_data = Photo.objects.get(pk=photo_data['id'])

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.language_preferences = validated_data.get('language_preferences', instance.language_preferences)

        if photo_data is not None:
            instance.photo = photo_data

        instance.save()

        return instance


class UserPasswordSerializer(serializers.Serializer):
    model = settings.AUTH_USER_MODEL

    password_current = CharField(required=True)
    password = CharField(required=True)
    password_confirmation = CharField(required=True, write_only=True)

    # class Meta:
    #     model = settings.AUTH_USER_MODEL
    #     fields = (
    #         'password_current', 'password', 'password_confirmation'
    #     )

    def validate_password_confirmation(self, value):
        data = self.get_initial()
        password1 = data.get('password')
        password2 = data.get('password_confirmation')

        if password1 != password2:
            raise ValidationError('Password and retype password should be same')

        return value
