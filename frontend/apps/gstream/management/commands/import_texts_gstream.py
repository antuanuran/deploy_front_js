import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import ClassName
from apps.gstream.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        for key, attrs in data.items():
            class_name_obj, _ = ClassName.objects.get_or_create(name=key)
            text_config_obj, _ = TextConfig.objects.update_or_create(
                class_name=class_name_obj, path=file_path
            )

            params_dict = {}
            for param, value in attrs.items():
                if param != "model":
                    params_dict[param] = value
                else:
                    params_dict["model"] = value
            model_name_obj, _ = ModelsName.objects.get_or_create(
                name=params_dict["model"]
            )

            TextAttrs.objects.update_or_create(
                text_config=text_config_obj,
                model_name=model_name_obj,
                text=params_dict["text"],
                text_for_onvif=params_dict["text_for_onvif"],
                text_for_telegram=params_dict["text_for_telegram"],
            )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_texts_gstream ../backend/gstream/configs/texts.yaml
