# Generated by Django 3.0.6 on 2020-09-09 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0005_distributor_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributor',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]