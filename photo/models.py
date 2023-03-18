from django.db import models
from django.utils.html import mark_safe


class Photo(models.Model):
    name = models.CharField(max_length=48, default=None, blank=True, null=True)
    attachment = models.FileField(upload_to='photo_files')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def attachment_tag(self):
        return mark_safe('<img src="%s" width="100" height="100" />' % self.attachment.url)

    attachment_tag.short_description = 'File'
    attachment_tag.allow_tags = True
