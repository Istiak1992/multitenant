from django.db import models


class Nationality(models.Model):
    name = models.CharField(max_length=64)
    country = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Nationality'
        verbose_name_plural = 'Nationalities'


class Fine(models.Model):
    amount = models.IntegerField()
    detail = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.detail

    class Meta:
        verbose_name = 'Fine'
        verbose_name_plural = 'Fines'
