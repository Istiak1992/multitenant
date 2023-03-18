from django_filters import rest_framework as filters
from .models import Distributor, DistributorWarning, WarningLog


class DistributorFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    type = filters.NumberFilter(field_name='distributor_type')
    inspector = filters.NumberFilter(field_name='inspector')

    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'updated', 'inspector')
        )
    )

    class Meta:
        model = Distributor
        fields = ['name', 'type']


class DistributorWarningFilterSet(filters.FilterSet):
    distributor = filters.NumberFilter()

    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'updated')
        )
    )

    class Meta:
        model = DistributorWarning
        fields = ['distributor']


class WarningLogFilterSet(filters.FilterSet):
    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('updated')
        )
    )

    class Meta:
        model = WarningLog
        fields = []
