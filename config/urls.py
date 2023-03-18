from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    NationalityListAPIView,
    FineListAPIView,
)

urlpatterns = [
    path('nationalities/', NationalityListAPIView.as_view()),
    path('fines/', FineListAPIView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
