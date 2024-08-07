import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.gstream.models import *
from apps.meta_data_processor.models import *
from apps.v_superuser.models import ClassName


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        for _, value in data.items():
            for class_name, color in value["colors"].items():
                class_name_obj, _ = ClassName.objects.get_or_create(name=class_name)
                color_obj, _ = ColorsConfig.objects.get_or_create(color_name=color)
                ColorsClassName.objects.update_or_create(
                    class_name=class_name_obj, color=color_obj
                )

            for number in value["classes"]:
                classes, _ = ClassesNumber.objects.update_or_create(number=number)

        for models_name, params in data.items():
            model_obj, _ = ModelsName.objects.get_or_create(name=models_name)
            models_config_obj, _ = ModelsConfig.objects.update_or_create(
                model_name=model_obj, path=file_path
            )

            keys_set = {
                "path",
                "description",
                "conf",
                "conf_keypoints",
                "conf_hand_up",
                "imgsz",
                "colors",
                "high_text",
                "size_points",
                "type",
                "classes",
                "task",
            }
            params_set = set({})
            for param, _ in params.items():
                params_set.add(param)
            set_result = keys_set - params_set
            for key in set_result:
                params[key] = False

            model_obj, _ = ModelParams.objects.update_or_create(
                models_config=models_config_obj,
                path=params["path"],
                conf=params["conf"],
                imgsz=params["imgsz"],
                high_text=params["high_text"],
                description=params["description"],
                conf_keypoints=params["conf_keypoints"],
                type=params["type"],
                size_points=params["size_points"],
                task=params["task"],
            )

            classes_list = []
            for numb in params["classes"]:
                class_numb, _ = ClassesNumber.objects.get_or_create(number=numb)
                classes_list.append(class_numb)

            colors_list = []
            for class_name, color in params["colors"].items():
                class_numb, _ = ColorsClassName.objects.get_or_create(
                    class_name__name=class_name
                )
                colors_list.append(class_numb)

            model_obj.classes.set(classes_list)
            model_obj.colors.set(colors_list)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_models_gstream ../backend/gstream/configs/models.yaml
