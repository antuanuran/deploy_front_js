from django.db import models


class Run(models.Model):
    class Param(models.TextChoices):
        RUN = "RUN"

    param = models.CharField(max_length=50, choices=Param.choices, unique=True)

    class Meta:
        verbose_name = "RUN"
        verbose_name_plural = "RUN"
