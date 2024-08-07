from django.contrib import admin
from .models import *


class TimeBetweenAttrslInline(admin.TabularInline):
    model = TimeBetweenSavingsAttrs
    extra = 0


@admin.register(TimeBetweenSaving)
class TimeBetweenSavingAdmin(admin.ModelAdmin):
    list_display = ["class_name", "path"]
    inlines = [TimeBetweenAttrslInline]
