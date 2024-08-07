import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.gstream.models import *


def save_file(file_path: str) -> None:
    data = {}

    for obj in ModelsConfig.objects.all():
        models_name = obj.model_name.name
        params_dict = {}

        params_obj = obj.configs.first()
        params_dict["path"] = params_obj.path
        params_dict["description"] = params_obj.description
        params_dict["conf_keypoints"] = params_obj.conf_keypoints
        params_dict["conf_hand_up"] = params_obj.conf_hand_up
        params_dict["imgsz"] = params_obj.imgsz
        params_dict["high_text"] = params_obj.high_text
        params_dict["size_points"] = params_obj.size_points
        params_dict["type"] = params_obj.type
        params_dict["task"] = params_obj.task

        classes_list = []
        for i in params_obj.classes.all():
            classes_list.append(i.number)
        params_dict["classes"] = classes_list

        colors_dict = {}
        for i in params_obj.colors.all():
            colors_dict[i.class_name.name] = i.color.color_name
        params_dict["colors"] = colors_dict

        data[models_name] = params_dict

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_colors_gstream ../backend/gstream/configs/colors.yaml
