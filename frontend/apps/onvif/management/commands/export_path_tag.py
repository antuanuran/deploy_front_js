import yaml
from yaml import Loader
from django.core.management import BaseCommand

from apps.onvif.models import *


def save_file(file_path: str) -> None:
    data = {}

    path_config = PathTag.objects.first()
    for i in path_config.tags.all():
        data[i.param] = i.name_method

    with open(file_path, "w") as file:
        yaml.dump(data, file)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_path_tag ../backend/onvif/configs/path_tag.yaml
