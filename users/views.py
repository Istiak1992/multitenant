from rest_framework import filters, permissions
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework import status
from auth.models import User
from .serializers import (
    UserListSerializer,
    UserCreateSerializer,
    UserDetailSerializer
)
from .filters import UserFilterSet
import django_excel as excel
from django.template.loader import get_template
from django.core.mail import EmailMessage


role_lang = {
    'inspector': 'مفتش',
    'distributor': 'موزع ',
    'supervisor': 'مشرف',
}

class UserListCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['pk', 'date_joined']

    def get_queryset(self):
        user_type = self.request.query_params.get('type', None)

        if user_type is not None:
            queryset = User.objects.filter(groups__name=user_type)
        else:
            queryset = User.objects.all()

        queryset = queryset.exclude(is_superuser=True)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        else:
            return UserCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user_filter = UserFilterSet(request.query_params, queryset=queryset)

        if request.query_params.get('export') == 'true':
            serializer = self.get_serializer(user_filter.qs, many=True)

            return self.export_list(data=serializer.data)

        page = self.paginate_queryset(user_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        if request.query_params.get('pagination') == 'false':
            data = self.get_serializer(user_filter.qs, many=True).data
            pagination = None
        else:
            data = paginated_data.data['results']
            pagination = paginated_data.data['pagination']

        return Response({
            'message': 'Success',
            'users': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)

    @staticmethod
    def export_list(data):
        report = [[
            'User Name',
            'Status'
        ]]

        for d in data:
            report.append([
                d['name'],
                'Active' if d['is_active'] else 'Inactive'
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'Users')

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'message': 'Validation Error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Send email to respective user
        try:
            ctx = {
                'role': request.data['role'],
                'name': request.data['name'],
                'email': request.data['email'],
                'password': request.data['password']
            }

            if request.user.language_preferences == 'EN':
                message = get_template('mail-user-add-success.html').render(ctx)
            else:
                ctx['role'] = role_lang[request.data['role']]

                message = get_template('mail-user-add-success-ar.html').render(ctx)

            msg = EmailMessage(
                'Welcome to Golden Brown QA Platform',
                message,
                'noreply@goldenbrown.sa',
                [request.data['email']],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except Exception as e:
            print('Exception occurred')
            print(e)

        return Response({
            'message': 'Success',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            'message': 'Success',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Send email to respective user
        try:
            ctx = {
                'role': request.data['role'],
                'name': request.data['name'],
                'email': request.data['email'],
                'password': request.data['password']
            }

            if request.user.language_preferences == 'EN':
                message = get_template('mail-user-add-success.html').render(ctx)
            else:
                message = get_template('mail-user-add-success-ar.html').render(ctx)

            msg = EmailMessage(
                'Welcome to Golden Brown QA Platform',
                message,
                'noreply@goldenbrown.sa',
                [request.data['email']],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except Exception as e:
            print('Exception occurred')
            print(e)

        return Response({
            'message': 'Successfully updated',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.delete()
        except Exception as e:
            return Response({
                'error': 'Some error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'Successfully deleted'
        }, status=status.HTTP_200_OK)
