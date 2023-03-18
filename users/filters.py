from django_filters import rest_framework as filters
from auth.models import User


class UserFilterSet(filters.FilterSet):
    name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')

    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'date_joined')
        )
    )

    class Meta:
        model = User
        fields = ['name']
