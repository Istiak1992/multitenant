# Generated by Django 3.0.6 on 2020-10-21 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0011_merge_20201018_0345'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='weight',
            field=models.IntegerField(default=0, max_length=2),
        ),
        migrations.AddField(
            model_name='inspectionchecklist',
            name='weight',
            field=models.IntegerField(default=0, max_length=2),
        ),
    ]
