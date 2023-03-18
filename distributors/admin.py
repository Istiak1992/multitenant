from django.contrib import admin
from .models import (
    City,
    DistributorType,
    Distributor,
    DistributorWarning,
    WarningLog
)


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')
    search_fields = ('name',)


class DistributorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')
    list_per_page = 10


class DistributorAdmin(admin.ModelAdmin):
    list_display = ('distributor_key', 'name', 'distributor_type', 'created')
    list_filter = ('distributor_type',)
    list_per_page = 10
    search_fields = ['name', 'distributor_type__name', 'distributor_key']


class DistributorWarningAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'amount', 'created')
    ordering = ('created',)
    search_fields = ('distributor__name', 'amount')


class WarningLogAdmin(admin.ModelAdmin):
    list_display = ('distributor_warning', 'title', 'generated_by', 'user')
    ordering = ('distributor_warning',)
    search_fields = ('distributor_warning__distributor__name', 'user__first_name')


admin.site.register(City, CityAdmin)
admin.site.register(DistributorType, DistributorTypeAdmin)
admin.site.register(Distributor, DistributorAdmin)
admin.site.register(DistributorWarning, DistributorWarningAdmin)
admin.site.register(WarningLog, WarningLogAdmin)
