from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    LoginView,
    LoginDistributorView,
    UserProfileView,
    ChangePasswordView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/distributor/', LoginDistributorView.as_view(), name='login_distributor'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('me/', UserProfileView.as_view(), name='profile_view'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password_view'),
]
