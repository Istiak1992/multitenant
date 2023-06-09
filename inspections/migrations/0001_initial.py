# Generated by Django 3.0.6 on 2020-05-11 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('photo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('distributors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_no', models.CharField(max_length=24)),
                ('total_mark', models.DecimalField(decimal_places=1, max_digits=3)),
                ('total_rating', models.DecimalField(decimal_places=2, max_digits=4)),
                ('finance_awb_no', models.CharField(blank=True, max_length=16, null=True)),
                ('finance_record_no', models.CharField(blank=True, max_length=16, null=True)),
                ('status', models.CharField(choices=[('100', 'Pending'), ('200', 'QA Approved'), ('300', 'Supervisor Approved'), ('400', 'Declined')], max_length=3)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('account_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspection_account_manager', to=settings.AUTH_USER_MODEL)),
                ('account_manager_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspection_account_manager_image', to='photo.Photo')),
                ('distributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspection_distributor', to='distributors.Distributor')),
                ('finance_awb_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspection_finance_awb_image', to='photo.Photo')),
                ('finance_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspection_finance_manager', to=settings.AUTH_USER_MODEL)),
                ('inspector', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspection_inspector', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InspectionChecklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail_en', models.CharField(max_length=256)),
                ('detail_ar', models.CharField(max_length=256)),
                ('response', models.NullBooleanField(default=None)),
                ('note', models.CharField(blank=True, max_length=256, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attachment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checklist_attachment', to='photo.Photo')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspection', to='inspections.Inspection')),
            ],
        ),
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail_en', models.CharField(max_length=256)),
                ('detail_ar', models.CharField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distributor_type', models.ManyToManyField(to='distributors.DistributorType')),
            ],
        ),
    ]
