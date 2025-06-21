from typing import Literal

from bot.schemas.base import Schema


class TelegramWebhookResponse(Schema):
    status: Literal["OK", "ERROR"] = "OK"
