from django.contrib import admin
from .models import (
    Checklist,
    Inspection,
    InspectionChecklist,
    InspectionNotification,
    InspectionLog
)


class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('detail_en', 'created')
    list_filter = ('distributor_type',)
    list_per_page = 10
    search_fields = ['detail_en']


class InspectionChecklistInline(admin.TabularInline):
    model = InspectionChecklist


class InspectionAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'distributor', 'inspector', 'status', 'created')
    list_filter = ('distributor__distributor_type', 'distributor', 'status', 'inspector',)
    list_per_page = 10
    search_fields = ['serial_no']
    inlines = (InspectionChecklistInline,)


class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'detail_en', 'created')
    ordering = ('inspection',)
    search_fields = ('inspection__serial_no',)


class InspectionNotificationAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'title', 'is_read', 'generated_by')
    ordering = ('inspection',)
    search_fields = ('inspection__serial_no', 'generated_by__first_name',)


class InspectionLogAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'title', 'generated_by')
    ordering = ('inspection',)
    search_fields = ('inspection__serial_no', 'title', 'generated_by',)


admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(Inspection, InspectionAdmin)
admin.site.register(InspectionNotification, InspectionNotificationAdmin)
admin.site.register(InspectionLog, InspectionLogAdmin)
