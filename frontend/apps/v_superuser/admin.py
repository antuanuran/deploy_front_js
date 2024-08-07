from django.contrib import admin
from .models import *


@admin.register(ClassName)
class ClassNameAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(ModelsName)
class ModelsNameAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(ClassesNumber)
class ClassesNumberAdmin(admin.ModelAdmin):
    list_display = ["number"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    list_display = ["name"]
