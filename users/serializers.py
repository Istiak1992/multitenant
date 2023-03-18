from auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.fields import CharField, EmailField, FileField
from photo.models import Photo
from photo.serializers import PhotoSerializer
from distributors.models import Distributor
from django.contrib.auth.models import Group


class UserGenericSerializer(serializers.ModelSerializer):
    name = CharField(required=True, source='first_name')

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'address', 'photo', 'is_active',)
        depth = 2


class UserListSerializer(serializers.ModelSerializer):
    name = CharField(required=True, source='first_name')

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'address', 'is_active', 'photo', 'date_joined'
        )
        depth = 2


class UserCreateSerializer(serializers.ModelSerializer):
    name = CharField(required=True, source='first_name')
    password_confirmation = CharField(required=True, write_only=True)
    address = CharField(allow_blank=True, allow_null=False, required=True)
    photo = PhotoSerializer(many=False, allow_null=True, required=False)
    role = CharField(required=True, write_only=True)
    profile_photo = FileField(required=False, allow_null=True, write_only=True)
    distributor_ids = CharField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'password', 'password_confirmation', 'address', 'is_active', 'photo', 'date_joined',
            'role', 'profile_photo', 'distributor_ids'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # Validate duplicate email with username
    def validate_email(self, value):
        data = self.get_initial()
        username = data.get('email')
        username_qs = User.objects.filter(username=username)

        if username_qs.exists():
            raise ValidationError('Email already exists')

        return value

    def validate_password_confirmation(self, value):
        data = self.get_initial()
        password1 = data.get('password')
        password2 = data.get('password_confirmation')

        if password1 != password2:
            raise ValidationError('Password and retype password should be same')

        return value

    def create(self, validated_data):
        profile_photo = validated_data.get('profile_photo')
        photo_data = None

        if profile_photo is not None:
            photo_serializer = PhotoSerializer(data={'name': 'profile_photo', 'attachment': profile_photo})

            if photo_serializer.is_valid():
                photo_serializer.save()
                photo_data = photo_serializer.data
                photo_data = Photo.objects.get(pk=photo_data['id'])

        user = User(
            username=validated_data.get('email'),
            email=validated_data.get('email'),
            password_plain=validated_data.get('password'),
            first_name=validated_data.get('first_name'),
            address=validated_data.get('address', None)
        )
        user.set_password(validated_data.get('password'))

        if photo_data is not None:
            user.photo = photo_data

        user.save()

        # Add to group
        group = Group.objects.get(name=validated_data['role'])
        user.groups.add(group)

        if validated_data.get('distributor_ids') is not None:
            distributor_ids = validated_data.get('distributor_ids').split(',')

            Distributor.objects.filter(inspector_id=user.pk).update(
                inspector_id=None
            )

            Distributor.objects.filter(pk__in=distributor_ids).update(
                inspector_id=user.pk
            )

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    name = CharField(required=True, source='first_name')
    photo = PhotoSerializer()
    profile_photo = FileField(required=False, allow_null=True, write_only=True)
    distributor_ids = CharField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'is_active', 'password', 'password_plain', 'address', 'language_preferences',
            'photo', 'profile_photo', 'distributor_ids'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

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

        if photo_data is not None:
            instance.photo = photo_data

        if validated_data.get('password') is not None:
            instance.set_password(validated_data.get('password'))
            instance.password_plain = validated_data.get('password', instance.password_plain)

        instance.save()

        if validated_data.get('distributor_ids') is not None:
            distributor_ids = validated_data.get('distributor_ids').split(',')

            Distributor.objects.filter(inspector_id=instance.pk).update(
                inspector_id=None
            )

            Distributor.objects.filter(pk__in=distributor_ids).update(
                inspector_id=instance.pk
            )

        return instance
