import yaml
from yaml import Loader
from django.core.management import BaseCommand

from apps.onvif.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        params = {"path": file_path}
        onvif_config, _ = PathTag.objects.update_or_create(**params)

        for param, name_method in data.items():
            PathTagUri.objects.update_or_create(
                onvif_config=onvif_config, param=param, name_method=name_method
            )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_path_tag ../backend/onvif/configs/path_tag.yaml
