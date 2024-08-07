import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import *
from apps.gstream.models import *


def save_file(file_path: str) -> None:
    data = {}
    attr = CommonAttrs.objects.first()
    data["logging_level"] = attr.logging_level
    data["status_bus_messages"] = attr.status_bus_messages
    data["level_debug"] = attr.level_debug
    data["time_live_client"] = attr.time_live_client
    data["port_for_onvif"] = attr.port_for_onvif
    data["draw_results_detect"] = attr.draw_results_detect
    data["draw_results_detect_full"] = attr.draw_results_detect_full
    data["type_protocol"] = attr.type_protocol
    data["telegram_works"] = attr.telegram_works
    data["onvif_works"] = attr.onvif_works
    data["ip_server"] = attr.ip_server
    data["device"] = attr.device
    data["start_rtsp_video_stream"] = attr.start_rtsp_video_stream
    data["device_id"] = attr.device_id
    data["fps"] = attr.fps
    data["image_width"] = attr.image_width
    data["port"] = attr.port
    data["stream_uri"] = attr.stream_uri

    cameras_list = []
    for i in attr.cameras.all():
        cameras_list.append(i.name)
    data["cameras_in_work"] = cameras_list

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        save_file(path)


# python manage.py export_colors_gstream ../backend/gstream/configs/colors.yaml
