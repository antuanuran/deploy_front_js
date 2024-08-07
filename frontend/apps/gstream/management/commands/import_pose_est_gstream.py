import yaml
from yaml import Loader
from django.core.management import BaseCommand
from apps.v_superuser.models import ClassName
from apps.gstream.models import *


def load_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=Loader)

        keypoints_list = [
            "nose",
            "left_eye",
            "right_eye",
            "left_ear",
            "right_ear",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_brush",
            "right_brush",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_foot",
            "right_foot",
            "face",
            "hands",
            "body",
            "legs",
        ]
        for point_name in keypoints_list:
            Points.objects.update_or_create(name=point_name)

        for name, values in data.items():
            pose_config_obj, _ = PoseEstConfig.objects.update_or_create(
                name_order=name, path=file_path
            )
            if name == "order_keypoints":
                for part, points_list in values.items():
                    pose, _ = PoseEstAttrs.objects.update_or_create(pose_config=pose_config_obj, part_skeleton=part)
                    points_all = []
                    for point in points_list:
                        points_all.append(Points.objects.first())
                    # print(points_all)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, *args, **options):
        load_file(path)


# python manage.py import_texts_gstream ../backend/gstream/configs/texts.yaml
