import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser import *

from apps.meta_data_processor.models import *


def save_file(file_path: str) -> None:
    data = {}

    for obj in TimeBetweenSaving.objects.all():
        class_name = obj.class_name.name
        dict_values = {}

        for values in obj.attrs.all():
            dict_values[values.interval_name] = values.interval_value
        data[class_name] = dict_values

        # data[obj.class_name.name] = {values.interval_name: values.interval_value for values in obj.attrs.all()}

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_meta_data ../backend/metadata_processor/configs/time_between_savings.yaml
