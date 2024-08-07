import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.meta_data_processor.models import *
from apps.v_superuser.models import ModelsName
from apps.v_superuser.models import ClassName


def load_file(file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.load(file, Loader=Loader)

        class_name_list = [
            "person",
            "face",
            "hands",
            "legs",
            "body",
            "gun",
            "knife",
            "bag",
            "balaclava",
            "concealing glasses",
            "hand",
            "medicine mask",
            "non-concealing glasses",
            "nothing",
            "scarf",
            "fall down",
            "helmet",
            "vest",
            "head",
            "hands_up",
        ]
        models_name_list = [
            "skeleton",
            "guns",
            "bags",
            "face_hiding",
            "human_fault",
            "siz",
        ]

        for class_name in class_name_list:
            ClassName.objects.update_or_create(name=class_name)

        for cmodel_name in models_name_list:
            ModelsName.objects.update_or_create(name=cmodel_name)

        for class_name, interval_values_list in data.items():
            class_name_obj, _ = ClassName.objects.get_or_create(name=class_name)
            time_between_config, _ = TimeBetweenSaving.objects.get_or_create(
                class_name=class_name_obj, path=file_path
            )

            for type_interval, value in interval_values_list.items():
                TimeBetweenSavingsAttrs.objects.get_or_create(
                    time_between_saving=time_between_config,
                    interval_name=type_interval,
                    interval_value=value,
                )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_meta_data ../backend/metadata_processor/configs/time_between_savings.yaml
