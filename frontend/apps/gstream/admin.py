from django.contrib import admin
from .models import *
from apps.v_superuser import *


# 1. Colors ********************************** #
class RGBInline(admin.TabularInline):
    model = RGB
    extra = 0


@admin.register(ColorsConfig)
class ColorsConfigAdmin(admin.ModelAdmin):
    list_display = ["color_name", "path"]
    inlines = [RGBInline]


# Colors ************************************** #


# 2. Models *********************************** #
class ModelParamsInline(admin.TabularInline):
    model = ModelParams
    extra = 0


@admin.register(ModelsConfig)
class ModelNameConfigAdmin(admin.ModelAdmin):
    list_display = ["model_name", "path"]
    inlines = [ModelParamsInline]


@admin.register(ColorsClassName)
class ColorsSkeletonAdmin(admin.ModelAdmin):
    list_display = ["class_name", "color"]


#    Models *********************************** #


class TextAttrsInline(admin.TabularInline):
    model = TextAttrs
    extra = 0


@admin.register(TextConfig)
class TextConfigAdmin(admin.ModelAdmin):
    list_display = ["class_name", "path"]
    inlines = [TextAttrsInline]


class CameraAttrsInline(admin.TabularInline):
    model = CameraAttrs
    extra = 0


@admin.register(CameraConfig)
class CameraConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "path"]
    inlines = [CameraAttrsInline]


class CommonAttrsInline(admin.TabularInline):
    model = CommonAttrs
    extra = 0


@admin.register(CommonConfig)
class CommonConfigAdmin(admin.ModelAdmin):
    list_display = ["path"]
    inlines = [CommonAttrsInline]


class PoseEstAttrsInline(admin.TabularInline):
    model = PoseEstAttrs
    extra = 0


@admin.register(PoseEstConfig)
class PoseEstConfigAdmin(admin.ModelAdmin):
    list_display = ["name_order", "path"]
    inlines = [PoseEstAttrsInline]
