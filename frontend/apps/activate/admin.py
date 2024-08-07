from django.contrib import admin
from .models import Run
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
import subprocess
from django.conf import settings
import os

# LOAD
from ..telegram.management.commands.import_telegram import (
    load_file as load_telegram_config,
)
from ..onvif.management.commands.import_path_tag import load_file as load_onvif_config
from ..meta_data_processor.management.commands.import_meta_data import (
    load_file as load_meta_data_config,
)
from ..gstream.management.commands.import_colors_gstream import (
    load_file as load_colors_gstream,
)
from ..gstream.management.commands.import_models_gstream import (
    load_file as load_models_gstream,
)
from ..gstream.management.commands.import_texts_gstream import (
    load_file as load_texts_gstream,
)
from ..gstream.management.commands.import_cameras_gstream import (
    load_file as load_cameras_gstream,
)
from ..gstream.management.commands.import_common_gstream import (
    load_file as load_common_gstream,
)
from ..gstream.management.commands.import_pose_est_gstream import (
    load_file as load_pose_est_gstream,
)


# SAVE
from ..telegram.management.commands.export_telegram import (
    save_file as save_telegram_config,
)
from ..onvif.management.commands.export_path_tag import save_file as save_path_tag_onvif
from ..meta_data_processor.management.commands.export_meta_data import (
    save_file as save_time_metadata,
)
from ..gstream.management.commands.export_colors_gstream import (
    save_file as save_colors_gstream,
)
from ..gstream.management.commands.export_models_gstream import (
    save_file as save_models_gstream,
)
from ..gstream.management.commands.export_texts_gstream import (
    save_file as save_texts_gstream,
)
from ..gstream.management.commands.export_cameras_gstream import (
    save_file as save_cameras_gstream,
)
from ..gstream.management.commands.export_common_gstream import (
    save_file as save_common_gstream,
)
from ..gstream.management.commands.export_pose_est_gstream import (
    save_file as save_pose_est_gstream,
)


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["load", "save", "run"]

    @admin.display(description="Start Gstreamer")
    def run(self, obj: Run):
        link = reverse("admin:activate", args=[obj.id])
        return mark_safe(
            f"<strong> <a style='color:#833756FF' href='{link}'>START</a> </strong>"
        )

    @admin.display(description="Save configs (ADMIN -> Yaml)")
    def save(self, obj: Run):
        link = reverse("admin:save", args=[obj.id])
        return mark_safe(
            f"<strong> <a style='color:#44794BFF' href='{link}'>SAVE</a> </strong>"
        )

    @admin.display(description="Load configs (Yaml -> ADMIN)")
    def load(self, obj: Run):
        link = reverse("admin:load", args=[obj.id])
        return mark_safe(
            f"<strong> <a style='color:44794BFF' href='{link}'>LOAD</a> </strong>"
        )

    def get_urls(self):
        urls = [
            path("<obj_id>/activate/", self.run_viewset, name="activate"),
            path("<obj_id>/save/", self.save_viewset, name="save"),
            path("<obj_id>/load/", self.load_viewset, name="load"),
        ] + super().get_urls()
        return urls

    def run_viewset(self, request, obj_id, *args, **kwargs):
        subprocess.call(
            ["docker", "compose", "down"], cwd=settings.MAIN_PROJECT_ROOT_FOLDER
        )
        subprocess.call(
            ["docker", "compose", "up", "-d"],
            cwd=settings.MAIN_PROJECT_ROOT_FOLDER,
        )
        return redirect(reverse("admin:activate_run_changelist"))

    def save_viewset(self, request, obj_id, *args, **kwargs):
        save_telegram_config(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "telegram/configs/telegram.yaml")
        )

        save_path_tag_onvif(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "onvif/configs/path_tag.yaml")
        )

        save_time_metadata(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "metadata_processor/configs/time_between_savings.yaml",
            )
        )

        save_colors_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/colors.yaml")
        )

        save_models_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/models.yaml")
        )

        save_texts_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/texts.yaml")
        )

        save_cameras_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/cameras.yaml")
        )

        save_common_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/common.yaml")
        )
        save_pose_est_gstream(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "gstream/configs/pose_est.yaml")
        )

        return redirect(reverse("admin:activate_run_changelist"))

    def load_viewset(self, request, obj_id, *args, **kwargs):
        load_telegram_config(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "telegram/configs/telegram.yaml")
        )

        load_onvif_config(
            os.path.join(settings.CONFIGS_ROOT_FOLDER, "onvif/configs/path_tag.yaml")
        )

        load_meta_data_config(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "metadata_processor/configs/time_between_savings.yaml",
            )
        )

        load_colors_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/colors.yaml",
            )
        )

        load_models_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/models.yaml",
            )
        )

        load_texts_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/texts.yaml",
            )
        )

        load_cameras_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/cameras.yaml",
            )
        )

        load_common_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/common.yaml",
            )
        )

        load_pose_est_gstream(
            os.path.join(
                settings.CONFIGS_ROOT_FOLDER,
                "gstream/configs/pose_est.yaml",
            )
        )

        return redirect(reverse("admin:activate_run_changelist"))
