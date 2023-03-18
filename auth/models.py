from django.db import models
from django.contrib.auth.models import AbstractUser
from photo.models import Photo


class User(AbstractUser):
    # LANGUAGE CHOICES
    LANGUAGE_ARABIC = 'AR'
    LANGUAGE_ENGLISH = 'EN'

    LANGUAGE_CHOICES = (
        (LANGUAGE_ARABIC, 'Arabic'),
        (LANGUAGE_ENGLISH, 'English'),
    )

    address = models.TextField(max_length=500, blank=True)
    password_plain = models.CharField(max_length=48, blank=True)
    photo = models.ForeignKey(
        Photo,
        related_name="user_photo",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )
    language_preferences = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default=LANGUAGE_ENGLISH)
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Meta:
        permissions = (
            ("can_add_supervisor", "Can add Supervisor"),
            ("can_add_inspector", "Can add Inspector"),
            ("can_add_distributor", "Can add Distributor"),
            ("role__supervisor", "Role Supervisor"),
            ("dashboard", "Dashboard"),
            ("notification_center", "Notification Center"),
            ("manage_profile", "Manage Profile"),
            ("inspectors_full", "Inspector Full"),
            ("distributors_full", "Distributor Full"),
            ("inspections", "Inspections"),
            ("qa_report", "QA Report"),
            ("dashboard_inspectors", "Dashboard Inspectors View"),
            ("dashboard_distributors", "Dashboard Distributors View"),
            ("dashboard_inspections", "Dashboard Inspections View"),
            ("role__manager", "Role QA"),
            ("supervisors_full", "Supervisors Full"),
            ("qa_inspection", "QA Inspection"),
            ("distributor_notification", "distributor_notification"),
            ("distributor_fine", "Distributor Fine"),
            ("reports", "Reports"),
            ("dashboard_supervisors", "Dashboard Supervisors"),
            ("role__account", "Role Account"),
            ("distributor_detail", "Distributor Detail"),
            ("dashboard_distributor_notifications", "Dashboard Distributor Notifications"),
            ("dashboard_distributor_warnings", "Dashboard Distributor Warnings"),
            ("role__finance", "Role Finance"),
            ("distributor_fine__finance", "Distributor Fine Finance"),
            ("role__legal", "Role Legal"),
            ("distributor_warning__legal", "Distributor Warning Legal"),
            ("role__inspector", "Role Inspector"),
            ("role__distributor", "Role Distributor"),
            ("distributor_visits", "Distributor Visits"),
        )
