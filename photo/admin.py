from django.contrib import admin
from .models import Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'attachment', 'attachment_tag',)
    fields = ('name', 'attachment', 'attachment_tag',)
    readonly_fields = ('attachment_tag',)
    list_per_page = 10


admin.site.register(Photo, PhotoAdmin)
