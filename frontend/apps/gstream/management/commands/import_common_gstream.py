import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *

from apps.gstream.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        common_config_obj, _ = CommonConfig.objects.update_or_create(path=file_path)
        cam, _ = CommonAttrs.objects.update_or_create(
            common_config=common_config_obj,
            logging_level=data["logging_level"],
            status_bus_messages=data["status_bus_messages"],
            level_debug=data["level_debug"],
            time_live_client=data["time_live_client"],
            port_for_onvif=data["port_for_onvif"],
            draw_results_detect=data["draw_results_detect"],
            draw_results_detect_full=data["draw_results_detect_full"],
            type_protocol=data["type_protocol"],
            telegram_works=data["telegram_works"],
            onvif_works=data["onvif_works"],
            ip_server=data["ip_server"],
            device=data["device"],
            start_rtsp_video_stream=data["start_rtsp_video_stream"],
            device_id=data["device_id"],
            fps=data["fps"],
            image_width=data["image_width"],
            # image_height=data["image_height"],
            port=data["port"],
            stream_uri=data["stream_uri"],
        )

        cameras_list = []
        for cam_name in data["cameras_in_work"]:
            camera_config_obj, _ = CameraConfig.objects.get_or_create(name=cam_name)
            cameras_list.append(camera_config_obj)
        cam.cameras.set(cameras_list)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_colors_gstream ../backend/gstream/configs/common.yaml
