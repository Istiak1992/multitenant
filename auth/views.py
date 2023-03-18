from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import (
    status,
    permissions
)
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserPasswordSerializer
)
from auth.models import User
from distributors.models import Distributor


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        lang = request.data.get('lang')
        lang = (lang if lang is not None else 'en').upper()

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({
                'error': 'Username or password is wrong'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check what role user have
        inspector = request.query_params.get('inspector', None) is not None
        user_is_inspector = user.has_perm('gbqa_auth.role__inspector')

        if inspector != user_is_inspector:
            return Response({
                'error': 'You are not authorized to login here'
            }, status=status.HTTP_400_BAD_REQUEST)

        user_is_distributor = user.has_perm('gbqa_auth.role__distributor')

        if user_is_distributor:
            return Response({
                'error': 'You are not authorized to login here'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user object from db
        user_data = User.objects.get(pk=user.pk)

        # Update language
        user_data.language_preferences = lang
        user_data.save()

        serializer = UserProfileSerializer(user_data)
        user_data = serializer.data
        user_data['permissions'] = user.get_all_permissions()

        # Get user tokens
        refresh = RefreshToken.for_user(user)

        token = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

        return Response({
            'user': user_data,
            'token': token
        }, status=status.HTTP_200_OK)


class LoginDistributorView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        distributor_key = request.data.get('username', None)

        # Get distributor
        distributor = Distributor.objects.filter(distributor_key=distributor_key).first()

        if distributor is None:
            return Response({
                'error': 'Distributor not found'
            }, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(
            request, username=distributor.distributor_user.username
        )

        if user is None:
            return Response({
                'error': 'Distributor user not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get user object from db
        user_data = User.objects.get(pk=user.pk)
        serializer = UserProfileSerializer(user_data)
        user_data = serializer.data
        user_data['permissions'] = user.get_all_permissions()

        # Get user tokens
        refresh = RefreshToken.for_user(user)

        token = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

        return Response({
            'user': user_data,
            'token': token,
            'distributor_id': distributor.pk
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user_data = User.objects.get(pk=request.user.id)
        serializer = UserProfileSerializer(user_data)
        user_data = serializer.data
        user_data['permissions'] = request.user.get_all_permissions()

        return Response({
            'user': user_data
        }, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            'message': 'Successfully updated',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    serializer_class = UserPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(serializer.data.get('password_current')):
            return Response({
                'errors': {
                    'password_current': [
                        'Wrong password.'
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(serializer.data.get('password'))
        request.user.save()

        return Response({
            'message': 'Successfully changed password'
        }, status=status.HTTP_200_OK)
