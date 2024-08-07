import yaml
from django.core.management import BaseCommand

from apps.telegram.models import *


def save_file(file_path: str) -> None:
    data = {}
    chats_admin_ids = []

    telegram_config = TelegramConfig.objects.first()
    data["token"] = telegram_config.token

    for chat_id in TelegramChatId.objects.all():
        chats_admin_ids.append(chat_id.value)
    data["chats_admin_ids"] = chats_admin_ids

    with open(file_path, "w") as file:
        yaml.dump(data, file)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_telegram ../backend/telegram/configs/telegram.yaml
