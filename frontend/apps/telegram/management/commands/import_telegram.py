import yaml
from yaml import Loader
from django.core.management import BaseCommand

from apps.telegram.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        params = {"path": file_path}
        relations = {}

        for key, value in data.items():
            if key in ("token",):
                params[key] = value
            else:
                relations[key] = value

    token_config, _ = TelegramConfig.objects.update_or_create(**params)
    for _, chats_ids_list in relations.items():
        for chat_id in chats_ids_list:
            TelegramChatId.objects.update_or_create(config=token_config, value=chat_id)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_telegram ../backend/telegram/configs/telegram.yaml
