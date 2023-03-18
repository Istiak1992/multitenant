from django.urls import path
from .views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='users-list'),
    path('<pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='users_detail'),
]
