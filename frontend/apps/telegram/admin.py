from django.contrib import admin
from .models import *


class TelegramChatIdInline(admin.TabularInline):
    model = TelegramChatId
    extra = 0


@admin.register(TelegramConfig)
class TelegramConfigAdmin(admin.ModelAdmin):
    list_display = ["path"]
    inlines = [TelegramChatIdInline]
