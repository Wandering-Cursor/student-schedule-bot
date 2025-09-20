import secrets

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
    secret_key = models.CharField(
        max_length=255,
        help_text="A secret key used to verify requests from Telegram.",
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
        return f"{self.webhook_url}/api/webhook/telegram/{self.uuid}/{self.secret_key}"

    class Meta(BaseModel.Meta):
        verbose_name = _("Telegram Bot")
        verbose_name_plural = _("Telegram Bots")

    def __str__(self) -> str:
        return f"Bot: {self.name}"

    def __repr__(self) -> str:
        return f'Bot(name="{self.name}", token="***", secret_key="***", webhook_url="{self.webhook_url}")'

    def generate_secret_key(self) -> str:
        """Generates a new secret key for the bot."""

        return secrets.token_urlsafe(32)

    def clean_secret_key(self) -> str:
        """Ensure the secret key is not empty."""
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()

        return self.secret_key

    def clean(self) -> None:
        self.clean_secret_key()
        return super().clean()
