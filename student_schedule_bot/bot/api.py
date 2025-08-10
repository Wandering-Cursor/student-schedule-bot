import json

import pydantic
from django.http import HttpRequest
from ninja import NinjaAPI, Schema

from bot.dependencies.telegram import get_bot as get_bot_instance
from bot.operations.telegram.bot import process_webhook_with_bot
from bot.schemas.telegram import TelegramWebhookResponse
from student_schedule_bot.logger import main_logger

api = NinjaAPI(
    title="Student Schedule Bot API",
    description="API for student schedule bot (basically webhooks and stuff)",
)


class BlankBody(Schema):
    pass


@api.post("/webhook/telegram/{bot_id}/{secret_key}")
async def telegram_webhook(
    request: HttpRequest,
    # Technically it's a WSGIRequest, but it's compatible with HttpRequest
    bot_id: pydantic.UUID4,
    secret_key: str,
    body: BlankBody,  # noqa: ARG001
) -> TelegramWebhookResponse:
    bot_instance = await get_bot_instance(
        bot_id=bot_id,
        secret_key=secret_key,
    )

    main_logger.debug(
        {
            "message": "Received Telegram webhook",
            "bot_id": bot_instance.uuid,
            "headers": dict(request.headers),
        }
    )

    await process_webhook_with_bot(
        bot_instance=bot_instance,
        update_data=json.loads(request.body),
    )

    return TelegramWebhookResponse(
        status="OK",
    )
