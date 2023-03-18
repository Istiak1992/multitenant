from django_filters import rest_framework as filters
from .models import Inspection, InspectionLog


class InspectionFilterSet(filters.FilterSet):
    date = filters.DateFilter(field_name='date_initial')
    distributor = filters.NumberFilter(field_name='distributor')
    distributorType = filters.NumberFilter(field_name='distributor__distributor_type')
    inspector = filters.NumberFilter(field_name='inspector')
    serial = filters.CharFilter(field_name='serial_no', lookup_expr='icontains')

    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('updated')
        )
    )

    class Meta:
        model = Inspection
        fields = ['date', 'distributor', 'distributorType', 'inspector', 'serial']


class InspectionNotificationFilterSet(filters.FilterSet):
    distributor = filters.NumberFilter(field_name='inspection__distributor')
    distributorType = filters.NumberFilter(field_name='inspection__distributor__distributor_type')

    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('updated')
        )
    )

    class Meta:
        model = Inspection
        fields = ['distributor', 'distributorType']


class InspectionLogFilterSet(filters.FilterSet):
    order_by_field = 'ordering'
    ordering = filters.OrderingFilter(
        fields=(
            ('updated')
        )
    )

    class Meta:
        model = InspectionLog
        fields = ['action_type']
