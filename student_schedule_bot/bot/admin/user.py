from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from bot.models.user import User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            "Group",
            {"fields": ("telegram_chat",)},
        ),
    )


admin.site.register(User, UserAdmin)
