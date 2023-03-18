from django.db import models
from photo.models import Photo
from auth.models import User


class City(models.Model):
    name = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'


class DistributorType(models.Model):
    name = models.CharField(max_length=48)
    description = models.CharField(max_length=256, default=None, blank=True, null=True)
    photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Distributor(models.Model):
    # CHOICES
    LANGUAGE_ARABIC = 'AR'
    LANGUAGE_ENGLISH = 'EN'

    LANGUAGE_CHOICES = (
        (LANGUAGE_ARABIC, 'Arabic'),
        (LANGUAGE_ENGLISH, 'English'),
    )

    # VISIT FREQUENCY
    FREQUENCY_DAILY = 'daily'
    FREQUENCY_WEEKLY = 'weekly'
    FREQUENCY_MONTHLY = 'monthly'

    FREQUENCY_CHOICES = (
        (FREQUENCY_DAILY, 'daily'),
        (FREQUENCY_WEEKLY, 'weekly'),
        (FREQUENCY_MONTHLY, 'monthly')
    )

    # DATABASE FIELDS
    name = models.CharField(max_length=48, default=None, blank=True, null=True)
    distributor_type = models.ForeignKey(DistributorType, related_name='distributor_type', on_delete=models.CASCADE)
    distributor_parent = models.ForeignKey(
        "self", related_name='parent', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=128, default=None, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    distributor_key = models.CharField(max_length=16, default=None, null=True)
    distributor_user = models.ForeignKey(User, related_name='distributor_user', on_delete=models.SET_NULL, null=True)
    contact_name = models.CharField(max_length=60, default=None, null=True)
    contact_email = models.CharField(max_length=60, default=None, null=True)
    contact_mobile = models.CharField(max_length=24, default=None, null=True)
    contact_nationality = models.CharField(max_length=48, default=None, null=True)
    account_manager = models.ForeignKey(User, related_name='account_manager', on_delete=models.SET_NULL, null=True)
    inspector = models.ForeignKey(User, related_name='inspector', on_delete=models.SET_NULL, null=True)
    visit_frequency = models.CharField(max_length=7, choices=FREQUENCY_CHOICES)
    language_preferences = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    sms_notification = models.BooleanField(default=False)
    total_visits = models.IntegerField(default=0)
    ratings = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DistributorWarning(models.Model):
    # STATUS CHOICES
    TYPE_GENERATED = 'gen'
    TYPE_FORCED = 'frc'

    TYPE_CHOICES = [
        (TYPE_GENERATED, 'Generated'),
        (TYPE_FORCED, 'Force Generated'),
    ]

    # STATUS CHOICES
    STATUS_PENDING = 100
    STATUS_QA_APPROVED = 200
    STATUS_ACCOUNT_APPROVED = 300
    STATUS_FINANCE_APPROVED = 500
    STATUS_REJECTED = 1000

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_QA_APPROVED, 'QA Approved'),
        (STATUS_ACCOUNT_APPROVED, 'Account Approved'),
        (STATUS_FINANCE_APPROVED, 'Finance Approved'),
        (STATUS_REJECTED, 'Rejected')
    ]

    # DATABASE FIELDS
    distributor = models.ForeignKey(Distributor, related_name='warning_distributor', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    account_manager = models.ForeignKey(
        User, related_name='warning_acm', on_delete=models.SET_NULL, blank=True, null=True)
    account_is_read = models.BooleanField(default=False)
    awb_image = models.ForeignKey(
        Photo, related_name='warning_awb_image', on_delete=models.SET_NULL, blank=True, null=True)
    awb_no = models.CharField(max_length=16, blank=True, null=True)
    finance_manager = models.ForeignKey(
        User, related_name='warning_finance_manager', on_delete=models.SET_NULL, blank=True, null=True)
    record_image = models.ForeignKey(
        Photo, related_name='warning_record_image', on_delete=models.SET_NULL, blank=True, null=True)
    record_no = models.CharField(max_length=16, blank=True, null=True)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True)
    is_final = models.BooleanField(default=False)
    notifications = models.ManyToManyField('inspections.InspectionNotification')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.distributor.name


class WarningLog(models.Model):
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
    distributor_warning = models.ForeignKey(DistributorWarning, related_name="wl_warning", on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=256, null=True)
    generated_by = models.CharField(max_length=3, choices=GENERATED_BY_CHOICES, default='usr')
    user = models.ForeignKey(User, related_name='wl_user', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=3, default=None, choices=LOG_TYPE_CHOICES)
    action_name = models.CharField(max_length=12, default=None, null=True)
    action_type = models.CharField(max_length=12, default=None, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
