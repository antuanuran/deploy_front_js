from django.contrib import admin
from .models import *


class PathTagIdInline(admin.TabularInline):
    model = PathTagUri
    extra = 0


@admin.register(PathTag)
class OnvifConfigAdmin(admin.ModelAdmin):
    list_display = ["path"]
    inlines = [PathTagIdInline]
