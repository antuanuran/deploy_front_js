from django.db import models
from apps.meta_data_processor.models import *
from apps.v_superuser.models import *

from django.db import models


# 1. Model - Colors **************************
class ColorsConfig(models.Model):
    class ColorNames(models.TextChoices):
        Maroon = "Maroon"
        Brown = "Brown"
        Olive = "Olive"
        Teal = "Teal"
        Navy = "Navy"
        Black = "Black"
        Red = "Red"
        Orange = "Orange"
        Yellow = "Yellow"
        Lime = "Lime"
        Green = "Green"
        Cyan = "Cyan"
        Blue = "Blue"
        Purple = "Purple"
        Magenta = "Magenta"
        Grey = "Grey"
        Pink = "Pink"
        Apricot = "Apricot"
        Beige = "Beige"
        Mint = "Mint"
        Lavender = "Lavender"
        White = "White"

    color_name = models.CharField(max_length=50, choices=ColorNames.choices)
    path = models.CharField(max_length=500)

    def __str__(self) -> str:
        return self.color_name

    class Meta:
        verbose_name = "1. COLORS"
        verbose_name_plural = "1. COLORS"


class RGB(models.Model):
    config = models.ForeignKey(
        ColorsConfig,
        on_delete=models.CASCADE,
        related_name="rgbs",
    )
    value = models.BigIntegerField()


# Model - Colors *****************************


# 2. Model - Models (START)**************************


class ColorsClassName(models.Model):
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    color = models.ForeignKey(ColorsConfig, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.class_name} | {self.color}"

    class Meta:
        verbose_name = "Colors / Class name (superuser)"
        verbose_name_plural = "Colors / Class name (superuser)"


class ModelsConfig(models.Model):
    model_name = models.ForeignKey(
        ModelsName, on_delete=models.CASCADE, related_name="configs"
    )
    path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.model_name.name

    class Meta:
        verbose_name = "2. MODELS"
        verbose_name_plural = "2. MODELS"


class ModelParams(models.Model):
    class TypeName(models.TextChoices):
        model_pose_yolo = "model_pose_yolo"
        need_skeleton = "need_skeleton"
        model_yolo = "model_yolo"

    models_config = models.ForeignKey(
        ModelsConfig, on_delete=models.CASCADE, related_name="configs"
    )

    path = models.CharField(max_length=50)
    description = models.CharField(
        max_length=50, default="Модель для обнаружения скелетов", blank=True, null=True
    )
    conf = models.FloatField()
    conf_keypoints = models.FloatField(blank=True, null=True)
    conf_hand_up = models.FloatField(blank=True, null=True)
    imgsz = models.IntegerField()
    colors = models.ManyToManyField(
        ColorsClassName, blank=True, null=True, related_name="+"
    )
    high_text = models.FloatField()
    size_points = models.IntegerField()
    type = models.CharField(max_length=30, choices=TypeName.choices)
    classes = models.ManyToManyField(
        ClassesNumber, blank=True, null=True, related_name="+"
    )
    task = models.CharField(max_length=50, blank=True, null=True)


# Model - Models (FINISH) **************************


class TextConfig(models.Model):
    class_name = models.ForeignKey(
        ClassName, on_delete=models.CASCADE, related_name="text_configs"
    )
    path = models.CharField(max_length=500)

    class Meta:
        verbose_name = "3. TEXTS"
        verbose_name_plural = "3. TEXTS"


class TextAttrs(models.Model):
    text_config = models.ForeignKey(
        TextConfig, on_delete=models.CASCADE, related_name="attrs"
    )

    model_name = models.ForeignKey(
        ModelsName, on_delete=models.CASCADE, related_name="model_attrs"
    )
    text = models.CharField(max_length=50)
    text_for_onvif = models.CharField(max_length=50)
    text_for_telegram = models.CharField(max_length=50)


# Cameras (Start) **************************


class CameraConfig(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "4. CAMERAS"
        verbose_name_plural = "4. CAMERAS"


class CameraAttrs(models.Model):
    class QualityType(models.TextChoices):
        low = "low"
        high = "high"

    camera_config = models.ForeignKey(
        CameraConfig, on_delete=models.CASCADE, related_name="configs"
    )
    name = models.CharField(max_length=50)
    location_rtspsrc = models.CharField(max_length=50, null=True, blank=True)
    location_description = models.CharField(max_length=50, null=True, blank=True)
    framerate = models.IntegerField(null=True, blank=True)
    model_names = models.ManyToManyField(
        ModelsName, blank=True, null=True, related_name="+"
    )
    hlssink_width = models.IntegerField(null=True, blank=True)
    hlssink_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    quality = models.CharField(
        max_length=50, choices=QualityType.choices, default=QualityType.low
    )
    opencv_output_width = models.IntegerField(null=True, blank=True)
    opencv_output_height = models.IntegerField(null=True, blank=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    user_pw = models.CharField(max_length=50, blank=True, null=True)
    profiles = models.ManyToManyField(Profile, blank=True, null=True, related_name="+")


# Cameras (Finish) **************************


class CommonConfig(models.Model):
    path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return self.path

    class Meta:
        verbose_name = "5. COMMON"
        verbose_name_plural = "5. COMMON"


class CommonAttrs(models.Model):
    class ProtocolType(models.TextChoices):
        rtsp_rts = "rtsp_rts"
        hls = "hls"

    class DeviceType(models.TextChoices):
        auto = "auto"
        cuda = "cuda"
        cpu = "cpu"

    common_config = models.ForeignKey(
        CommonConfig, on_delete=models.CASCADE, related_name="attrs"
    )
    cameras = models.ManyToManyField(
        CameraConfig, blank=True, null=True, related_name="+"
    )
    logging_level = models.CharField(max_length=50)
    status_bus_messages = models.BooleanField(default=True)
    level_debug = models.IntegerField(blank=True, null=True)
    time_live_client = models.IntegerField(blank=True, null=True)
    port_for_onvif = models.IntegerField(blank=True, null=True)
    draw_results_detect = models.BooleanField(default=True)
    draw_results_detect_full = models.BooleanField(default=False)
    type_protocol = models.CharField(
        max_length=50, choices=ProtocolType.choices, default=ProtocolType.rtsp_rts
    )
    telegram_works = models.BooleanField(default=True)
    onvif_works = models.BooleanField(default=True)
    ip_server = models.CharField(max_length=50, blank=True, null=True)
    device = models.CharField(
        max_length=50, choices=DeviceType.choices, default=DeviceType.auto
    )
    start_rtsp_video_stream = models.BooleanField(default=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    fps = models.IntegerField(blank=True, null=True)
    image_width = models.IntegerField(blank=True, null=True)
    # image_height = models.IntegerField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    stream_uri = models.CharField(max_length=50, blank=True, null=True)


class PoseEstConfig(models.Model):
    name_order = models.CharField(max_length=50)
    path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return self.name_order

    class Meta:
        verbose_name = "6. POSE EST"
        verbose_name_plural = "6. POSE EST"


class PoseEstAttrs(models.Model):
    pose_config = models.ForeignKey(
        PoseEstConfig, on_delete=models.CASCADE, related_name="pose_attrs"
    )
    part_skeleton = models.CharField(max_length=500, blank=True, null=True)
    points = models.ManyToManyField(Points, blank=True, null=True, related_name="+")
