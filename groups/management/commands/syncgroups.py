from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
import json


class Command(BaseCommand):
    help = 'Add user groups & permissions'

    def handle(self, *args, **options):
        groups = [
            {
                'name': 'supervisor',
                'permissions': [
                    'role__supervisor',
                    'dashboard',
                    'notification_center',
                    'manage_profile',
                    'inspectors_full',
                    'distributors_full',
                    'inspections',
                    'qa_report',
                    'dashboard_inspectors',
                    'dashboard_distributors',
                    'dashboard_inspections'
                ]
            },
            {
                'name': 'qa',
                'permissions': [
                    'role__manager',
                    'dashboard',
                    'notification_center',
                    'manage_profile',
                    'inspectors_full',
                    'supervisors_full',
                    'qa_inspection',
                    'distributor_notification',
                    'distributor_fine',
                    'reports',
                    'dashboard_inspectors',
                    'dashboard_supervisors',
                    'dashboard_inspections'
                ]
            },
            {
                'name': 'finance',
                'permissions': [
                    'role__finance',
                    'dashboard',
                    'dashboard_distributor_warnings',
                    'manage_profile',
                    'distributor_fine__finance',
                ]
            },
            {
                'name': 'account',
                'permissions': [
                    'role__account',
                    'dashboard',
                    'notification_center',
                    'manage_profile',
                    'distributor_detail',
                    'dashboard_distributor_notifications',
                    'dashboard_distributor_warnings',
                ]
            },
            {
                'name': 'legal',
                'permissions': [
                    'role__legal',
                    'manage_profile',
                    'distributor_warning__legal',
                ]
            },
            {
                'name': 'inspector',
                'permissions': [
                    'role__inspector'
                ]
            },
            {
                'name': 'distributor',
                'permissions': [
                    'role__distributor',
                    'distributor_visits'
                ]
            },
        ]

        for gr in groups:
            group, created = Group.objects.update_or_create(
                name=gr["name"],
                defaults={'name': gr["name"]},
            )

            for perm in gr["permissions"]:
                permission = Permission.objects.get(codename=perm)

                group.permissions.add(permission)

            self.stdout.write(self.style.SUCCESS('Successfully sync group of "%s"' % gr['name']))
