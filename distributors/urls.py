from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    CityListAPIView,
    DistributorTypeListView,
    DistributorListCreateAPIView,
    DistributorRetrieveUpdateDestroyAPIView,
    DistributorUserGenerateAPIView,
    DistributorWarningListAPIView,
    DistributorWarningLogListView,
    DistributorWarningActionUpdateAPIView
)

urlpatterns = [
    path('cities/', CityListAPIView.as_view()),
    path('types/', DistributorTypeListView.as_view()),
    path('distributors/', DistributorListCreateAPIView.as_view(), name='distributors_list'),
    path('distributors/generate/', DistributorUserGenerateAPIView.generate, name='distributor_user_generate'),
    path('distributors/<pk>', DistributorRetrieveUpdateDestroyAPIView.as_view(), name='distributors_detail'),

    path('warnings/', DistributorWarningListAPIView.as_view()),
    path('warnings/<pk>/logs', DistributorWarningLogListView.as_view()),
    path(
        'warnings/<pk>/actions',
        DistributorWarningActionUpdateAPIView.as_view(),
        name='distributor-warnings-action'
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
