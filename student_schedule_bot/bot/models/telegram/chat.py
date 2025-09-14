from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models.base import BaseModel


class TelegramChat(BaseModel):
    chat_id = models.BigIntegerField(
        verbose_name=_("Chat ID"),
        unique=True,
        help_text=_("Unique identifier for the chat. Can be a user ID or group ID."),
    )

    title = models.CharField(
        verbose_name=_("Title"),
        max_length=512,
        help_text=_("Title of the chat. For groups, this is the group name."),
    )
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=255,
        blank=True,
        help_text=_("Username of the chat, if available."),
    )

    additional_info = models.JSONField(
        verbose_name=_("Additional Info"),
        blank=True,
        help_text=_("Additional information about the chat, stored as JSON."),
    )

    class Meta(BaseModel.Meta):
        verbose_name = _("Telegram Chat")
        verbose_name_plural = _("Telegram Chats")
