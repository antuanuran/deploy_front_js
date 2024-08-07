import yaml
from yaml import Loader
from django.core.management import BaseCommand

from apps.gstream.models import *


def save_file(file_path: str) -> None:
    data = {}

    for obj in TextConfig.objects.all():
        params_dict = {}
        text_obj = obj.attrs.first()
        params_dict["model"] = text_obj.model_name.name
        params_dict["text"] = text_obj.text
        params_dict["text_for_onvif"] = text_obj.text_for_onvif
        params_dict["text_for_telegram"] = text_obj.text_for_telegram

        data[obj.class_name.name] = params_dict

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_texts_gstream ../backend/gstream/configs/texts.yaml
