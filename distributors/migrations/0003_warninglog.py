# Generated by Django 3.0.6 on 2020-05-11 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('distributors', '0002_distributorwarning'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarningLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('subtitle', models.CharField(max_length=256, null=True)),
                ('generated_by', models.CharField(choices=[('sys', 'System'), ('usr', 'User')], default='usr', max_length=3)),
                ('type', models.CharField(choices=[('scs', 'Success'), ('err', 'Error'), ('wrn', 'Warning')], default=None, max_length=3)),
                ('action_name', models.CharField(default=None, max_length=12, null=True)),
                ('action_type', models.CharField(default=None, max_length=12, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distributor_warning', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wl_warning', to='distributors.DistributorWarning')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wl_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]