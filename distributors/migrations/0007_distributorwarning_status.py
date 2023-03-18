# Generated by Django 3.0.6 on 2020-09-21 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0006_distributor_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributorwarning',
            name='status',
            field=models.IntegerField(choices=[(100, 'Generated'), (200, 'Incomplete')], null=True),
        ),
    ]