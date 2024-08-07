from django.contrib import admin
from django.urls import path


class CustomSite(admin.AdminSite):
    site_title = "Hi-Tech Security"

    site_header = "Hi-Tech Security"

    index_title = "КОМПЛЕКСНЫЕ СИСТЕМЫ БЕЗОПАСНОСТИ"

    def get_urls(self):
        custom_urls = [
            # path(
            #     "ndvi-notification/",
            #     self.admin_view(views.NdviNotificationsView.as_view()),
            #     name="ndvi-notification",
        ]
        default_urls = super().get_urls()
        return custom_urls + default_urls
