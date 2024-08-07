import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *
from apps.gstream.models import *


def save_file(file_path: str) -> None:
    data = {}
    for obj in ColorsConfig.objects.all():
        color_name = obj.color_name
        values_list = []
        for obj_value in obj.rgbs.all():
            values_list.append(obj_value.value)
        data[color_name] = values_list

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_colors_gstream ../backend/gstream/configs/colors.yaml
