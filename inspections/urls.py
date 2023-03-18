from django.urls import path
from .views import (
    InspectionGeneratorAPIView,
    InspectionCronAPIView,
    InspectionListAPIView,
    InspectionRetrieveUpdateDestroyAPIView,
    InspectionActionUpdateAPIView,
    InspectionNotificationListAPIView,
    InspectionNotificationLogListAPIView,
    InspectionRetrievePdfAPIView,
    InspectionNotificationActionUpdateAPIView,
    InspectionView,
    InspectionChecklistListView
)

urlpatterns = [
    path('checklists', InspectionChecklistListView.as_view()),
    path('generate', InspectionGeneratorAPIView.generate, name='inspection-generator'),
    path('daily-update', InspectionCronAPIView.daily_update, name='inspection-daily-update'),
    path('reschedule', InspectionGeneratorAPIView.reschedule, name='inspection-reschedule'),
    path('reports', InspectionView.get_report, name='qa_report'),
    path('notifications', InspectionNotificationListAPIView.as_view(), name='inspections-notifications-list'),
    path(
        'notifications/<pk>/logs',
        InspectionNotificationLogListAPIView.as_view(),
        name='inspections-notifications-log'
    ),
    path(
        'notifications/<inspection__pk>/actions',
        InspectionNotificationActionUpdateAPIView.as_view(),
        name='inspections-notifications-action'
    ),
    path(
        'inspection-logs',
        InspectionNotificationLogListAPIView.as_view(),
        name='inspections-log'
    ),
    path('', InspectionListAPIView.as_view(), name='inspections-list'),
    path('<pk>', InspectionRetrieveUpdateDestroyAPIView.as_view(), name='inspections-detail'),
    path('<pk>/pdf', InspectionRetrievePdfAPIView.as_view(), name='inspections-detail-pdf'),
    path('<pk>/actions', InspectionActionUpdateAPIView.as_view(), name='inspections-action'),
]
