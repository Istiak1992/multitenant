from django.contrib import admin
from .models import (
    Nationality,
    Fine
)


class NationalityAdmin(admin.ModelAdmin):
    list_display = ('country', 'name')
    ordering = ('name',)
    search_fields = ('name',)


class FineAdmin(admin.ModelAdmin):
    list_display = ('detail', 'amount')
    ordering = ('amount',)
    search_fields = ('detail',)


admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Fine, FineAdmin)
