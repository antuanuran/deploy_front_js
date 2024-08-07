from django.db import models
from apps.v_superuser.models import ClassName


class TimeBetweenSaving(models.Model):
    class_name = models.ForeignKey(
        ClassName, on_delete=models.CASCADE, related_name="time_betweens"
    )
    path = models.CharField(max_length=500)

    class Meta:
        verbose_name = "TIME BETWEEN SAVINGS"
        verbose_name_plural = "TIME BETWEEN SAVINGS"


class TimeBetweenSavingsAttrs(models.Model):
    class NameIntervals(models.TextChoices):
        save_interval = "save_interval"
        telegram_send_interval = "telegram_send_interval"
        frontend_send_interval = "frontend_send_interval"
        onvif_send_interval = "onvif_send_interval"
        mqtt_send_interval = "mqtt_send_interval"

    time_between_saving = models.ForeignKey(
        TimeBetweenSaving, on_delete=models.CASCADE, related_name="attrs"
    )
    interval_name = models.CharField(max_length=30, choices=NameIntervals.choices)
    interval_value = models.IntegerField()
