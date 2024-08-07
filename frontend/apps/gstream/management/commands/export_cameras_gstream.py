import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.gstream.models import *


def save_file(file_path: str) -> None:
    data = {}

    for obj in CameraConfig.objects.all():
        cam_name = obj.name
        params_dict = {}

        params_obj_all = obj.configs.first()
        params_dict["name"] = cam_name
        params_dict["location_rtspsrc"] = params_obj_all.location_rtspsrc
        params_dict["location_description"] = params_obj_all.location_description
        params_dict["framerate"] = params_obj_all.framerate
        params_dict["hlssink_width"] = params_obj_all.hlssink_width
        params_dict["video_width"] = params_obj_all.video_width
        params_dict["video_height"] = params_obj_all.video_height
        params_dict["port"] = params_obj_all.port
        params_dict["quality"] = params_obj_all.quality
        params_dict["opencv_output_width"] = params_obj_all.opencv_output_width
        params_dict["opencv_output_height"] = params_obj_all.opencv_output_height
        params_dict["user_id"] = params_obj_all.user_id
        params_dict["user_pw"] = params_obj_all.user_pw

        models_list = []
        for i in params_obj_all.model_names.all():
            models_list.append(i.name)
        params_dict["models"] = models_list

        profiles_list = []
        for i in params_obj_all.profiles.all():
            profiles_list.append(i.name)
        params_dict["profiles"] = profiles_list

        data[cam_name] = params_dict

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_colors_gstream ../backend/gstream/configs/colors.yaml
