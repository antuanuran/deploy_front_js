from django.db import models


class TelegramConfig(models.Model):
    path = models.CharField(
        max_length=500, default="/backend/telegram/configs/telegram.yaml"
    )
    token = models.CharField(max_length=255)

    class Meta:
        verbose_name = "TELEGRAM"
        verbose_name_plural = "TELEGRAM"


class TelegramChatId(models.Model):
    config = models.ForeignKey(
        TelegramConfig,
        on_delete=models.CASCADE,
        related_name="chats_admin_ids",
    )
    value = models.BigIntegerField()
