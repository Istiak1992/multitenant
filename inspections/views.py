from django.db.models import Prefetch, Max, Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import date
from rest_framework import filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView
)
from rest_framework.views import APIView
from rest_framework import status
from .models import (
    Checklist,
    Inspection,
    InspectionChecklist,
    InspectionNotification,
    InspectionLog
)
from .serializers import (
    ChecklistSerializer,
    InspectionListSerializer,
    InspectionSerializer,
    InspectionUpdateSerializer,
    InspectionNotificationListSerializer,
    InspectionLogListSerializer,
    InspectionLogUpdateSerializer
)
from .filters import (
    InspectionFilterSet,
    InspectionNotificationFilterSet,
    InspectionLogFilterSet
)
from .utils import render_to_pdf
from distributors.models import (
    Distributor,
    DistributorWarning,
    WarningLog
)
from photo.models import Photo
import django_excel as excel



class InspectionGeneratorAPIView:
    @api_view(['GET'])
    @permission_classes([permissions.AllowAny])
    def generate(request):
        req_date = request.query_params.get('date', None)

        if req_date is None:
            req_date = date.today().strftime("%Y-%m-%d")

        distributors = Distributor.objects.all()
        count = 0

        for distributor in distributors:
            if distributor.inspector is None:
                continue

            inspection = Inspection.objects.filter(
                date_initial=req_date,
                distributor=distributor
            ).first()

            if inspection is not None:
                continue

            max_id = Inspection.objects.aggregate(Max('id'))

            if max_id['id__max'] is None:
                max_id['id__max'] = "0"

            try:
                new_serial = 'SN ' + str(int(max_id['id__max']) + 1).zfill(6)
            except ValueError:
                new_serial = None

            inspection = Inspection(
                serial_no=new_serial,
                date_initial=req_date,
                distributor=distributor,
                inspector=distributor.inspector,
                account_manager=distributor.account_manager,
                total_mark=0,
                total_rating=0,
                status=Inspection.STATUS_PENDING
            )
            inspection.save()

            checklists = Checklist.objects.filter(distributor_type=distributor.distributor_type).values()

            for checklist in checklists:
                inspection_checklist = InspectionChecklist(
                    inspection=inspection,
                    detail_en=checklist['detail_en'],
                    detail_ar=checklist['detail_ar'],
                    weight=checklist['weight']
                )
                inspection_checklist.save()

            count += 1

        return Response({
            'message': 'Successfully added ' + str(count) + ' inspections'
        }, status=status.HTTP_200_OK)

    @api_view(['POST'])
    @permission_classes([])
    def reschedule(request):
        date = request.data.get('date')
        distributors = request.data.get('distributors')

        # Validation check
        if date is None:
            return Response({
                'error': 'Date field is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if distributors is None:
            return Response({
                'error': 'Distributors field is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find all the inspections with distributor id
        inspections = Inspection.objects.filter(
            Q(status=Inspection.STATUS_PENDING) |
            Q(status__range=[Inspection.STATUS_INCOMPLETE, Inspection.STATUS_INCOMPLETE_NOTIFIED])
        ).filter(distributor__in=distributors)

        counter = len(inspections)

        inspections.update(date_initial=date, status=Inspection.STATUS_PENDING)

        return Response({
            'message': 'Successfully rescheduled ' + str(counter) + ' inspections'
        }, status=status.HTTP_200_OK)


class InspectionCronAPIView:
    @api_view(['GET'])
    @permission_classes([permissions.AllowAny])
    def daily_update(request):
        Inspection.objects.filter(status=Inspection.STATUS_PENDING, date_initial__lt=date.today())\
            .update(status=Inspection.STATUS_INCOMPLETE)

        return Response({
            'message': 'Successfully updated incomplete inspections'
        }, status=status.HTTP_200_OK)


class InspectionListAPIView(ListAPIView):
    queryset = Inspection.objects.all()
    serializer_class = InspectionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['serial_no']

    def get_queryset(self):
        user_is_inspector = self.request.user.has_perm('gbqa_auth.role__inspector')

        queryset = Inspection.objects.all()

        if user_is_inspector:
            queryset = queryset.filter(inspector=self.request.user.pk)

        if self.request.query_params.get('date_range') is not None:
            date_range = self.request.query_params.get('date_range').split('~')

            if len(date_range) == 2:
                queryset = queryset.filter(date_initial__range=[date_range[0], date_range[1]])

        if self.request.query_params.get('status') is not None:
            query_status = self.request.query_params.get('status').split(',')
            qs = []

            for st in query_status:
                if st == 'pending':
                    qs.append(Q(status=Inspection.STATUS_PENDING))
                elif st == 'incomplete':
                    qs.append(Q(status__range=[Inspection.STATUS_INCOMPLETE, Inspection.STATUS_INCOMPLETE_NOTIFIED]))
                elif st == 'complete':
                    qs.append(Q(status__range=[Inspection.STATUS_COMPLETED, Inspection.STATUS_SUPERVISOR_DECLINED]))

            status_q = Q()

            for q in qs:
                status_q = status_q | q

            queryset = queryset.filter(status_q)

        queryset = queryset.prefetch_related(Prefetch(
            'checklists',
            queryset=InspectionChecklist.objects.order_by('id',)
        ))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        inspection_filter = InspectionFilterSet(request.query_params, queryset=queryset)

        if request.query_params.get('export') == 'true':
            serializer = self.get_serializer(inspection_filter.qs, many=True)

            return self.export_list(data=serializer.data)

        page = self.paginate_queryset(inspection_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return Response({
            'message': 'Success',
            'inspections': paginated_data.data['results'],
            'pagination': paginated_data.data['pagination']
        }, status=status.HTTP_200_OK)

    @staticmethod
    def export_list(data):
        report = [[
            'Serial No.',
            'Date',
            'Distributor Name',
            'Distributor Type',
            'Inspector Name',
            'Mark'
        ]]

        for d in data:
            report.append([
                d['serial_no'],
                d['date_initial'],
                d['distributor']['name'],
                d['distributor']['distributor_type']['name'],
                d['inspector']['name'] if d['inspector'] is not None else '',
                d['total_mark'],
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'All-Visits')


class InspectionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inspection.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            'message': 'Success',
            'inspection': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Request validation
        if request.user.pk != instance.inspector.pk:
            return Response({
                'error': 'You are not authorized to submit this form'
            }, status=status.HTTP_400_BAD_REQUEST)

        pending_statuses = [
            Inspection.STATUS_PENDING,
            Inspection.STATUS_INCOMPLETE,
            Inspection.STATUS_INCOMPLETE_NOTIFIED,
            Inspection.STATUS_INCOMPLETE_REASSIGNED
        ]

        if instance.status not in pending_statuses:
            return Response({
                'error': 'This form has already been submitted'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InspectionUpdateSerializer(instance, data=request.data, partial=False)

        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Get inspection data again
        inspection = Inspection.objects.get(pk=instance.pk)
        inspection_serializer = self.get_serializer(inspection)

        # Store Inspection Notification
        inspection_notification = InspectionNotification(
            inspection=inspection,
            title=inspection.distributor.name + ' visit score is ' + str(inspection.total_mark) + '%',
            role='supervisor',
            generated_by=request.user
        )
        inspection_notification.save()

        # Store Inspection Log
        inspection_log = InspectionLog(
            inspection=inspection,
            title=inspection.distributor.name + ' visit score is ' + str(inspection.total_mark) + '%',
            subtitle='',
            generated_by=InspectionLog.GEN_BY_SYSTEM,
            user=request.user,
            type=InspectionLog.TYPE_INFO,
            # action_name=None,
            # action_type=None
        )
        inspection_log.save()

        # Generate Fine for lower score TODO: load mark and amount from DB
        if inspection.total_mark < 80:
            distributor_warning = DistributorWarning(
                distributor=inspection.distributor,
                amount=500,
                account_manager=inspection.account_manager,
                type=DistributorWarning.TYPE_GENERATED,
                status=DistributorWarning.STATUS_PENDING
            )
            distributor_warning.save()

            # Store Warning Log
            warning_log = WarningLog(
                distributor_warning=distributor_warning,
                title=distributor_warning.distributor.name + ' has been fined SR ' + str(distributor_warning.amount),
                subtitle='',
                generated_by=WarningLog.GEN_BY_SYSTEM,
                user=request.user,
                type=WarningLog.TYPE_INFO,
                # action_name=None,
                # action_type=None
            )
            warning_log.save()

            distributor_warning.notifications.add(inspection_notification)

        return Response({
            'message': 'Successfully updated',
            'inspection': inspection_serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != Inspection.STATUS_INCOMPLETE:
            return Response({
                'error': 'Only incomplete inspections can be deleted'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.delete()
        except Exception as e:
            return Response({
                'error': 'Some error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'Successfully deleted'
        }, status=status.HTTP_200_OK)


class InspectionRetrievePdfAPIView(RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inspection.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # getting the template
        pdf = render_to_pdf('inspection.html', serializer.data)

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')


class InspectionActionUpdateAPIView(UpdateAPIView):
    lookup_field = 'pk'
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inspection.objects.all()

    def update(self, request, *args, **kwargs):
        action_set = {
            'account_image': 'gbqa_auth.role__account',
            'reassign': 'gbqa_auth.inspectors_full',
            'set_reminder': 'gbqa_auth.inspectors_full',
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

        if request.data.get('action') == 'account_image':
            if request.data.get('account_image'):
                instance.account_manager_image = Photo.objects.get(pk=request.data.get('account_image'))
        elif request.data.get('action') == 'reassign':
            if request.data.get('inspector_id'):
                instance.inspector_id = request.data.get('inspector_id')
                instance.status = Inspection.STATUS_INCOMPLETE_REASSIGNED
        elif request.data.get('action') == 'set_reminder':
            instance.status = Inspection.STATUS_INCOMPLETE_NOTIFIED

        instance.save()

        serializer = self.get_serializer(instance)

        return Response({
            'message': 'Success',
            'inspection': serializer.data
        }, status=status.HTTP_200_OK)


# Get Inspections list (limit, inspector_name, dist_type, dist_name, incomplete)

# Updated status (incomplete_notify, incomplete_reassign, )


class InspectionNotificationListAPIView(ListAPIView):
    queryset = InspectionNotification.objects.all()
    serializer_class = InspectionNotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        role = 'supervisor' if self.request.user.has_perm('gbqa_auth.role__supervisor') else None

        if role is None:
            role = 'manager' if self.request.user.has_perm('gbqa_auth.role__manager') else None

        if role is None:
            role = 'account' if self.request.user.has_perm('gbqa_auth.role__account') else None

        queryset = InspectionNotification.objects.filter(role=role).order_by('-updated')

        if self.request.query_params.get('report') is not None:
            if self.request.query_params.get('report_type') == 'escalation':
                queryset = InspectionNotification.objects\
                    .filter(
                        inspection__in=list(
                            InspectionLog.objects.filter(
                                type=InspectionLog.TYPE_SUCCESS,
                                action_type='manager'
                            ).values_list('inspection_id', flat=True)
                        )
                    ).order_by('-updated')
            elif self.request.query_params.get('report_type') == 'all':
                queryset = InspectionNotification.objects.order_by('-updated')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        inspection_filter = InspectionNotificationFilterSet(request.query_params, queryset=queryset)
        page = self.paginate_queryset(inspection_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return Response({
            'message': 'Success',
            'notifications': paginated_data.data['results'],
            'pagination': paginated_data.data['pagination']
        }, status=status.HTTP_200_OK)


class InspectionNotificationLogListAPIView(ListAPIView):
    queryset = InspectionLog.objects.all()
    serializer_class = InspectionLogListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        queryset = InspectionLog.objects

        if 'pk' in self.kwargs:
            queryset = queryset.filter(inspection__pk=self.kwargs['pk'])

        return queryset.order_by('created')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        inspection_filter = InspectionLogFilterSet(request.query_params, queryset=queryset)

        if request.query_params.get('export') == 'true':
            serializer = self.get_serializer(inspection_filter.qs, many=True)

            if request.query_params.get('action_type') == 'manager':
                return self.export_list_escalation(data=serializer.data)
            elif request.query_params.get('action_type') == 'account':
                return self.export_list_notification(data=serializer.data)

        page = self.paginate_queryset(inspection_filter.qs)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return Response({
            'message': 'Success',
            'logs': paginated_data.data['results'],
            'pagination': paginated_data.data['pagination']
        }, status=status.HTTP_200_OK)

    @staticmethod
    def export_list_escalation(data):
        report = [[
            'Serial No.',
            'Inspector Name',
            'Distributor Name',
            'Supervisor Name',
            'Escalation Date'
        ]]

        for d in data:
            report.append([
                d['inspection']['serial_no'],
                d['inspection']['inspector']['name'],
                d['inspection']['distributor']['name'],
                d['user']['name'],
                d['created'],
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'Escalations')

    @staticmethod
    def export_list_notification(data):
        report = [[
            'Notification Date',
            'Serial No.',
            'Distributor Name',
            'Supervisor Name',
            'Status'
        ]]

        for d in data:
            report.append([
                d['created'],
                d['inspection']['serial_no'],
                d['inspection']['distributor']['name'],
                d['user']['name'],
                'Approved' if d['status'] == 'Success' else 'Rejected',
            ])

        sheet = excel.pe.Sheet(report)

        return excel.make_response(sheet, 'xlsx', 200, 'Notifications')


class InspectionNotificationActionUpdateAPIView(UpdateAPIView):
    lookup_field = 'inspection__pk'
    # serializer_class = InspectionLogUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InspectionNotification.objects.all()

    def update(self, request, *args, **kwargs):
        action_set = {
            'supervisor_approve': 'gbqa_auth.role__supervisor',
            'supervisor_reject': 'gbqa_auth.role__supervisor',
            'manager_approve': 'gbqa_auth.role__manager',
            'manager_reject': 'gbqa_auth.role__manager',
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

        if request.data.get('action') == 'supervisor_approve':
            instance.role = 'manager'
            instance.save()

            # Store Inspection Log
            inspection_log = InspectionLog(
                inspection=instance.inspection,
                title='Approved by Supervisor',
                subtitle='',
                generated_by=InspectionLog.GEN_BY_USER,
                user=request.user,
                type=InspectionLog.TYPE_SUCCESS,
                action_type='manager'
            )
            inspection_log.save()
        elif request.data.get('action') == 'supervisor_reject':
            if request.data.get('reject_reason') is None:
                return Response({
                    'error': 'A specific reason is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            instance.role = None
            instance.save()

            # Store Inspection Log
            inspection_log = InspectionLog(
                inspection=instance.inspection,
                title='Rejected by Supervisor',
                subtitle=request.data.get('reject_reason'),
                generated_by=InspectionLog.GEN_BY_USER,
                user=request.user,
                type=InspectionLog.TYPE_ERROR,
                action_type='supervisor'
            )
            inspection_log.save()
        elif request.data.get('action') == 'manager_approve':
            instance.role = 'account'
            instance.save()

            # Store Inspection Log
            inspection_log = InspectionLog(
                inspection=instance.inspection,
                title='Approved by QA Manager',
                subtitle='',
                generated_by=InspectionLog.GEN_BY_USER,
                user=request.user,
                type=InspectionLog.TYPE_SUCCESS,
                action_type='account'
            )
            inspection_log.save()
        elif request.data.get('action') == 'manager_reject':
            if request.data.get('reject_reason') is None:
                return Response({
                    'error': 'A specific reason is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            instance.role = 'supervisor'
            instance.save()

            # Store Inspection Log
            inspection_log = InspectionLog(
                inspection=instance.inspection,
                title='Rejected by QA Manager',
                subtitle=request.data.get('reject_reason'),
                generated_by=InspectionLog.GEN_BY_USER,
                user=request.user,
                type=InspectionLog.TYPE_ERROR,
                action_type='manager'
            )
            inspection_log.save()

        return Response({
            'message': 'Successfully updated action'
        }, status=status.HTTP_200_OK)


class InspectionView(APIView):
    @csrf_exempt
    @api_view(['GET'])
    def get_report(request):
        data = []
        distributors = Distributor.objects

        if request.query_params.get('distributor', None) is not None:
            distributors = distributors.filter(pk=request.query_params.get('distributor', None))

        if request.query_params.get('distributor_type', None) is not None:
            distributors = distributors.filter(distributor_type=request.query_params.get('distributor_type', None))

        if request.query_params.get('city', None) is not None:
            distributors = distributors.filter(city=request.query_params.get('city', None))

        distributors = distributors.all().values()

        for distributor in distributors:
            data.append(distributor)

            # Get checklists counter
            false_counter = InspectionChecklist.objects \
                .filter(inspection__distributor_id=distributor['id'], response=False).values('detail_en') \
                .annotate(total=Count('detail_en'))

            data[-1]['counter'] = false_counter

        return Response(data, 200)


class InspectionChecklistListView(ListAPIView):
    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response({
            'message': 'Success',
            'checklists': serializer.data
        }, status=status.HTTP_200_OK)
