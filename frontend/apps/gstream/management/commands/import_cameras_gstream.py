import yaml
from yaml import Loader
from django.core.management import BaseCommand

from apps.gstream.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        for name_cam, values in data.items():
            camera_config, _ = CameraConfig.objects.update_or_create(
                name=name_cam, path=file_path
            )

            for name in values["profiles"]:
                Profile.objects.update_or_create(name=name)

            related_params = {}
            params = {"camera_config": camera_config}
            for param, value in values.items():
                if param == "name":
                    params["name"] = value
                elif param == "location_rtspsrc":
                    params["location_rtspsrc"] = value
                elif param == "location_description":
                    params["location_description"] = value
                elif param == "framerate":
                    params["framerate"] = value
                elif param == "hlssink_width":
                    params["hlssink_width"] = value
                elif param == "hlssink_height":
                    params["hlssink_height"] = value
                elif param == "video_width":
                    params["video_width"] = value
                elif param == "video_height":
                    params["video_height"] = value
                elif param == "port":
                    params["port"] = value
                elif param == "quality":
                    params["quality"] = value
                elif param == "opencv_output_width":
                    params["opencv_output_width"] = value
                elif param == "opencv_output_height":
                    params["opencv_output_height"] = value
                elif param == "user_id":
                    params["user_id"] = value
                elif param == "user_pw":
                    params["user_pw"] = value

                elif param == "models":
                    related_params["models"] = value

                elif param == "profiles":
                    related_params["profiles"] = value

            cam, _ = CameraAttrs.objects.update_or_create(**params)

            models_list = []
            for mod in related_params["models"]:
                model_name_obj, _ = ModelsName.objects.get_or_create(name=mod)
                models_list.append(model_name_obj)

            profiles_list = []
            for prof in related_params["profiles"]:
                profile_obj, _ = Profile.objects.get_or_create(name=prof)
                profiles_list.append(profile_obj)

            cam.model_names.set(models_list)
            cam.profiles.set(profiles_list)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_texts_gstream ../backend/gstream/configs/texts.yaml
