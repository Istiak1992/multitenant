import time
from rest_framework import permissions, filters
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import City, DistributorType, Distributor, DistributorWarning, WarningLog
from .serializers import (
    CitySerializer,
    DistributorTypeSerializer,
    DistributorListSerializer,
    DistributorGenericSerializer,
    DistributorCreateSerializer,
    DistributorDetailSerializer,
    DistributorWarningSerializer,
    DistributorWarningLogSerializer
)
from .filters import (
    DistributorFilterSet,
    DistributorWarningFilterSet,
    WarningLogFilterSet
)
from photo.models import Photo
import django_excel as excel
from django.template.loader import get_template
from django.core.mail import EmailMessage
from users.serializers import UserCreateSerializer


class CityListAPIView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'message': 'Success',
            'cities': serializer.data,
        }, status=status.HTTP_200_OK)


class DistributorTypeListView(ListAPIView):
    queryset = DistributorType.objects.all()
    serializer_class = DistributorTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['pk', 'name']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'message': 'Success',
            'distributorTypes': serializer.data,
        }, status=status.HTTP_200_OK)


class DistributorListCreateAPIView(ListCreateAPIView):
    queryset = Distributor.objects.filter(is_active=True)
    serializer_class = DistributorListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Distributor.objects.filter(is_active=True)
        current_user = self.request.user

        if current_user.has_perm('gbqa_auth.role__inspector'):
            queryset = queryset.filter(inspector=current_user.pk)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.request.user.has_perm('gbqa_auth.role__inspector'):
                return DistributorGenericSerializer

            return DistributorListSerializer
        else:
            return DistributorListSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            distributor_filter = DistributorFilterSet(request.query_params, queryset=queryset)
            page = self.paginate_queryset(distributor_filter.qs)
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.query_params.get('pagination') == 'false':
            data = self.get_serializer(distributor_filter.qs, many=True).data
            pagination = None
        else:
            data = paginated_data.data['results']
            pagination = paginated_data.data['pagination']

        if request.query_params.get('export') == 'true':
            serializer = self.get_serializer(distributor_filter.qs, many=True)

            return self.export_list(data=serializer.data)

        return Response({
            'message': 'Success',
            'distributors': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)

    @staticmethod
    def export_list(data):
        report = [[
            'Distributor Name',
            'Distributor Type',
            'Frequency',
            'Total Visit',
            'Rating'
        ]]

        for d in data:
            report.append([
                d['name'],
                d['distributor_type']['name'],
                d['visit_frequency'],
                d['total_visits'],
                d['ratings']
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'Distributors')

    def create(self, request, *args, **kwargs):
        serializer = DistributorCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'message': 'Validation Error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        key = self.get_distributor_key()

        # Create Distributor User
        user_serializer = UserCreateSerializer(data={
            'name': serializer.validated_data['name'],
            'email': key + '@gbqa-dist.com',
            'password': 'SomethingElse',
            'password_confirmation': 'SomethingElse',
            'address': serializer.validated_data['address'],
            'role': 'distributor',
        })

        if not user_serializer.is_valid():
            return Response({
                'message': 'Validation Error',
                'errors': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        distributor_user = user_serializer.save()

        # Create distributor key
        serializer.save(
            distributor_key=key,
            distributor_user=distributor_user
        )

        # Send email to respective user
        try:
            ctx = {
                'name': request.data['name'],
                'distributor_id': key,
            }
            message = get_template('mail-dist-add-success.html').render(ctx)
            msg = EmailMessage(
                'Welcome to Golden Brown QA Platform',
                message,
                'noreply@goldenbrown.sa',
                [request.data['contact_email']],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except Exception as e:
            print('Exception occurred')
            print(e)

        return Response({
            'message': 'Success',
            'distributor': serializer.data
        }, status=status.HTTP_200_OK)

    @staticmethod
    def get_distributor_key(distributor_last=None):
        if distributor_last is None:
            # Get latest distributor
            distributor_last = Distributor.objects.latest('id')

        distributor_last_id = str(distributor_last.id + 1)

        key = 'gb-dist-'

        if len(distributor_last_id) < 6:
            key = key + str(round(time.time_ns() / 100))[-(6 - len(distributor_last_id)):]

        return key + distributor_last_id


class DistributorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = DistributorDetailSerializer
    queryset = Distributor.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            'message': 'Success',
            'distributor': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            distributor_type_id=request.data.get('distributor_type', None),
            distributor_parent_id=request.data.get('distributor_parent', None),
            city_id=request.data.get('city', None),
            account_manager_id=request.data.get('account_manager', None),
            inspector_id=request.data.get('inspector', None)
        )

        return Response({
            'message': 'Successfully updated',
            'distributor': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.is_active = False
            instance.save()
        except Exception as e:
            return Response({
                'error': 'Some error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'Successfully deleted'
        }, status=status.HTTP_200_OK)


class DistributorUserGenerateAPIView:
    @api_view(['GET'])
    @permission_classes([permissions.AllowAny])
    def generate(self):
        distributors = Distributor.objects.filter(distributor_key=None)

        for distributor in distributors:
            key = DistributorListCreateAPIView.get_distributor_key(distributor)

            # Create Distributor User
            user_serializer = UserCreateSerializer(data={
                'name': distributor.name,
                'email': key + '@gbqa-dist.com',
                'password': 'SomethingElse',
                'password_confirmation': 'SomethingElse',
                'address': distributor.address if distributor.address is not None else 'Address',
                'role': 'distributor',
            })

            if not user_serializer.is_valid():
                print(user_serializer.errors)

                continue

            distributor_user = user_serializer.save()

            # Create distributor key
            distributor.distributor_key = key
            distributor.distributor_user = distributor_user
            distributor.save()

        return Response({
            'counter': len(distributors)
        }, status=status.HTTP_200_OK)


class DistributorWarningListAPIView(ListAPIView):
    queryset = DistributorWarning.objects.all()
    serializer_class = DistributorWarningSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['pk', 'distributor', 'created', 'updated']

    def get_queryset(self):
        queryset = DistributorWarning.objects

        if self.request.query_params.get('type') == 'report':
            if self.request.query_params.get('report') == 'manager':
                queryset = queryset.filter(status__gt=DistributorWarning.STATUS_PENDING)
            elif self.request.query_params.get('report') == 'account':
                queryset = queryset.filter(
                    status__gt=DistributorWarning.STATUS_QA_APPROVED,
                    status__lt=DistributorWarning.STATUS_REJECTED
                )

            return queryset

        if self.request.user.has_perm('gbqa_auth.role__manager'):
            queryset = queryset.filter(status=DistributorWarning.STATUS_PENDING)
        elif self.request.user.has_perm('gbqa_auth.role__account'):
            queryset = queryset.filter(
                status__range=[DistributorWarning.STATUS_QA_APPROVED, DistributorWarning.STATUS_FINANCE_APPROVED]
            )
        elif self.request.user.has_perm('gbqa_auth.role__finance'):
            if self.request.query_params.get('type') == 'history':
                queryset = queryset.filter(status=DistributorWarning.STATUS_FINANCE_APPROVED)
            else:
                queryset = queryset.filter(
                    status__range=[
                        DistributorWarning.STATUS_ACCOUNT_APPROVED, DistributorWarning.STATUS_FINANCE_APPROVED
                    ]
                )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        item_filter = DistributorWarningFilterSet(request.query_params, queryset=queryset)

        if request.query_params.get('export') == 'true':
            serializer = self.get_serializer(item_filter.qs, many=True)

            return self.export_list(data=serializer.data)

        page = self.paginate_queryset(item_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return Response({
            'message': 'Success',
            'warnings': paginated_data.data['results'],
            'pagination': paginated_data.data['pagination']
        }, status=status.HTTP_200_OK)

    @staticmethod
    def export_list(data):
        report = [[
            'Warning Date',
            'Warning Text',
            'Distributor Name',
            'Distributor Type',
            'Status'
        ]]

        for d in data:
            report.append([
                d['created'],
                d['amount'] + ' SR',
                d['distributor']['name'],
                d['distributor']['distributor_type']['name'],
                'Approved' if d['status'] < 1000 else 'Rejected'
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'Warnings')


class DistributorWarningLogListView(ListAPIView):
    queryset = WarningLog.objects.all()
    serializer_class = DistributorWarningLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        queryset = WarningLog.objects.filter(distributor_warning__id=self.kwargs['pk']).order_by('created')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        warning_filter = WarningLogFilterSet(request.query_params, queryset=queryset)
        page = self.paginate_queryset(warning_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return Response({
            'message': 'Success',
            'logs': paginated_data.data['results'],
            'pagination': paginated_data.data['pagination']
        }, status=status.HTTP_200_OK)


class DistributorWarningActionUpdateAPIView(UpdateAPIView):
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated]
    queryset = DistributorWarning.objects.all()

    def update(self, request, *args, **kwargs):
        action_set = {
            'manager_approve': 'gbqa_auth.role__manager',
            'manager_reject': 'gbqa_auth.role__manager',
            'mark_final': 'gbqa_auth.role__manager',
            'stop_dealing': 'gbqa_auth.role__manager',
            'account_awb': 'gbqa_auth.role__account',
            'mark_as_read': 'gbqa_auth.role__account',
            'finance_record': 'gbqa_auth.role__finance'
        }

        # Check user has permission
        try:
            user_has_permission = self.request.user.has_perm(
                action_set[request.data.get('action')]
            )
        except KeyError:
            user_has_permission = False

        if not user_has_permission:
            return Response({
                'error': 'You are not authorized to take this action'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()

        if request.data.get('action') == 'manager_approve':
            instance.status = DistributorWarning.STATUS_QA_APPROVED
            instance.save()

            # Store Warning Log
            warning_log = WarningLog(
                distributor_warning=instance,
                title='Approved by QA Manager',
                subtitle='',
                generated_by=WarningLog.GEN_BY_USER,
                user=request.user,
                type=WarningLog.TYPE_SUCCESS
            )
            warning_log.save()
        elif request.data.get('action') == 'manager_reject':
            if request.data.get('reject_reason') is None:
                return Response({
                    'error': 'A specific reason is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            instance.status = DistributorWarning.STATUS_REJECTED
            instance.save()

            # Store Warning Log
            warning_log = WarningLog(
                distributor_warning=instance,
                title='Rejected by QA Manager',
                subtitle=request.data.get('reject_reason'),
                generated_by=WarningLog.GEN_BY_USER,
                user=request.user,
                type=WarningLog.TYPE_ERROR
            )
            warning_log.save()
        elif request.data.get('action') == 'mark_final':
            instance.is_final = True
            instance.save()
        elif request.data.get('action') == 'account_awb':
            if request.data.get('awb_image'):
                instance.awb_image = Photo.objects.get(pk=request.data.get('awb_image'))

            instance.awb_no = request.data.get('awb_no')
            instance.status = DistributorWarning.STATUS_ACCOUNT_APPROVED
            instance.save()
        elif request.data.get('action') == 'mark_as_read':
            instance.account_is_read = True
            instance.save()
        elif request.data.get('action') == 'finance_record':
            instance.finance_manager = request.user

            if request.data.get('record_image'):
                instance.record_image = Photo.objects.get(pk=request.data.get('record_image'))

            instance.record_no = request.data.get('record_no')
            instance.status = DistributorWarning.STATUS_FINANCE_APPROVED
            instance.save()

        return Response({
            'message': 'Successfully updated action'
        }, status=status.HTTP_200_OK)
