from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models.base import BaseModel


class Bot(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the bot, used for identification.",
    )

    token = models.CharField(
        max_length=255,
        unique=True,
        help_text="The token used to authenticate the bot with the Telegram API.",
    )

    webhook_url = models.URLField(
        max_length=1024,
        blank=True,
        help_text=(
            "The URL where the bot will receive updates from Telegram. If empty, the bot will not use webhooks."
        ),
    )

    @property
    def full_webhook_url(self) -> str:
        """Returns the full webhook URL including the token."""
        return f"{self.webhook_url}/api/webhook/telegram/{self.uuid}"

    class Meta(BaseModel.Meta):
        verbose_name = _("Telegram Bot")
        verbose_name_plural = _("Telegram Bots")
