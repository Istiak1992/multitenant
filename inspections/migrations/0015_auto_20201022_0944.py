# Generated by Django 3.0.6 on 2020-10-22 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0014_auto_20201022_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectionlog',
            name='action_name',
            field=models.CharField(blank=True, default=None, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='inspectionlog',
            name='action_type',
            field=models.CharField(blank=True, default=None, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='inspectionlog',
            name='subtitle',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
