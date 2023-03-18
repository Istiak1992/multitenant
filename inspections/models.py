from django.db import models
from datetime import date
from auth.models import User
from photo.models import Photo
from distributors.models import (
    DistributorType,
    Distributor,
    DistributorWarning
)


class Checklist(models.Model):
    detail_en = models.CharField(max_length=256)
    detail_ar = models.CharField(max_length=256)
    distributor_type = models.ManyToManyField(DistributorType)
    weight = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.detail_en


class Inspection(models.Model):
    # STATUS CHOICES
    STATUS_PENDING = 100
    STATUS_INCOMPLETE = 200
    STATUS_INCOMPLETE_REASSIGNED = 220
    STATUS_INCOMPLETE_NOTIFIED = 240
    STATUS_COMPLETED = 300
    STATUS_SUPERVISOR_APPROVED = 400
    STATUS_SUPERVISOR_DECLINED = 600
    STATUS_DELETED = 1000

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_INCOMPLETE, 'Incomplete'),
        (STATUS_INCOMPLETE_REASSIGNED, 'Reassigned'),
        (STATUS_INCOMPLETE_NOTIFIED, 'Notified'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_SUPERVISOR_APPROVED, 'Supervisor Approved'),
        (STATUS_SUPERVISOR_DECLINED, 'Supervisor Declined'),
        (STATUS_DELETED, 'Deleted')
    ]

    # DATABASE FIELDS
    serial_no = models.CharField(max_length=24)
    date_initial = models.DateField(default=date.today, null=False)
    distributor = models.ForeignKey(Distributor, related_name='inspection_distributor', on_delete=models.CASCADE)
    inspector = models.ForeignKey(User, related_name='inspection_inspector', on_delete=models.SET_NULL, null=True)
    total_mark = models.IntegerField(default=0)
    total_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    account_manager = models.ForeignKey(
        User, related_name='inspection_account_manager', on_delete=models.SET_NULL, blank=True, null=True)
    account_manager_image = models.ForeignKey(
        Photo, related_name='inspection_account_manager_image', on_delete=models.SET_NULL, blank=True, null=True)
    account_is_read = models.BooleanField(default=False)
    finance_manager = models.ForeignKey(
        User, related_name='inspection_finance_manager', on_delete=models.SET_NULL, blank=True, null=True)
    finance_awb_image = models.ForeignKey(
        Photo, related_name='inspection_finance_awb_image', on_delete=models.SET_NULL, blank=True, null=True)
    finance_awb_no = models.CharField(max_length=16, blank=True, null=True)
    finance_record_no = models.CharField(max_length=16, blank=True, null=True)
    finance_is_read = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serial_no

    class Meta:
        ordering = ['-updated']


class InspectionChecklist(models.Model):
    # DATABASE FIELDS
    inspection = models.ForeignKey(Inspection, related_name="checklists", on_delete=models.CASCADE)
    detail_en = models.CharField(max_length=256)
    detail_ar = models.CharField(max_length=256)
    response = models.NullBooleanField(default=None)
    note = models.CharField(max_length=256, blank=True, null=True)
    attachment = models.ForeignKey(
        Photo,
        related_name="checklist_attachment",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )
    weight = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.detail_en


class InspectionNotification(models.Model):
    # DATABASE FIELDS
    inspection = models.ForeignKey(Inspection, related_name="in_inspection", on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    is_read = models.BooleanField(default=False)
    role = models.CharField(max_length=48, default=None, blank=True, null=True)
    generated_by = models.ForeignKey(User, related_name='in_gen_by', on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class InspectionLog(models.Model):
    # LOG TYPE CHOICES
    TYPE_INFO = 'inf'
    TYPE_SUCCESS = 'scs'
    TYPE_ERROR = 'err'
    TYPE_WARNING = 'wrn'

    LOG_TYPE_CHOICES = [
        (TYPE_INFO, 'Info'),
        (TYPE_SUCCESS, 'Success'),
        (TYPE_ERROR, 'Error'),
        (TYPE_WARNING, 'Warning')
    ]

    # GENERATED BY CHOICES
    GEN_BY_SYSTEM = 'sys'
    GEN_BY_USER = 'usr'

    GENERATED_BY_CHOICES = [
        (GEN_BY_SYSTEM, 'System'),
        (GEN_BY_USER, 'User'),
    ]

    # DATABASE FIELDS
    inspection = models.ForeignKey(Inspection, related_name="il_inspection", on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=256, null=True, blank=True)
    generated_by = models.CharField(max_length=3, choices=GENERATED_BY_CHOICES, default='usr')
    user = models.ForeignKey(User, related_name='il_user', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=3, default=None, choices=LOG_TYPE_CHOICES)
    action_name = models.CharField(max_length=12, default=None, null=True, blank=True)
    action_type = models.CharField(max_length=12, default=None, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
