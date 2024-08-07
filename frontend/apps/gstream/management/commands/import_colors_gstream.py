import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.gstream.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        for color_name, values_list in data.items():
            config, _ = ColorsConfig.objects.get_or_create(
                color_name=color_name, path=file_path
            )
            config.rgbs.all().delete()
            for value in values_list:
                RGB.objects.create(config=config, value=value)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_colors_gstream ../backend/gstream/configs/colors.yaml
