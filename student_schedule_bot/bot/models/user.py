from django.contrib.auth.models import AbstractUser
from django.db import models

from bot.models.telegram.chat import TelegramChat


class User(AbstractUser):
    telegram_chat = models.ForeignKey(
        TelegramChat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
