from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist
from .models import User


class DistributorModelBackend(BaseBackend):
    def authenticate(self, request, username=None):
        user = User.objects.get(username=username)

        if not user.has_perm('gbqa_auth.role__distributor'):
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
