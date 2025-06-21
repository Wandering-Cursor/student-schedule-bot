from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from bot.admin.base import BaseAdmin
from bot.models.telegram.bot import Bot
from bot.operations.telegram.webhook import set_webhook

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


@admin.register(Bot)
class TelegramBotAdmin(BaseAdmin):
    fieldsets = [
        *BaseAdmin.fieldsets,
        (
            _("Bot"),
            {
                "fields": [
                    "name",
                    "token",
                    "webhook_url",
                ]
            },
        ),
    ]

    list_display = [
        *BaseAdmin.list_display[: BaseAdmin.FIRST_FIELD_PADDING],
        "name",
        "short_token",
        *BaseAdmin.list_display[BaseAdmin.LAST_FIELD_PADDING :],
    ]

    FIRST_FIELD_PADDING = BaseAdmin.FIRST_FIELD_PADDING + 2

    def short_token(self, obj: "Bot") -> str:
        """Returns a shortened version of the token."""
        return f"{obj.token[:5]}...{obj.token[-5:]}" if obj.token else ""

    actions = [*BaseAdmin.actions, "set_webhook_url"]

    @admin.action(description=_("Set webhook URL for selected bots"))
    def set_webhook_url(
        self,
        request,  # noqa: ANN001
        queryset: "QuerySet[Bot]",
    ) -> None:
        """Action to set the webhook URL for selected bots."""
        for bot in queryset:
            result = set_webhook(bot)

            if not result:
                self.message_user(
                    request,
                    _("Failed to set webhook for bot: {bot_name}. Check logs for details.").format(
                        bot_name=bot.name,
                    ),
                    level="error",
                )

        self.message_user(
            request,
            _("Webhook URL set for selected bots."),
            level="success",
        )
