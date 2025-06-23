import pydantic
from django.http import HttpRequest
from ninja import NinjaAPI

from bot.dependencies.telegram import get_bot
from bot.schemas.telegram import TelegramWebhookResponse
from student_schedule_bot.logger import main_logger

api = NinjaAPI(
    title="Student Schedule Bot API",
    description="API for student schedule bot (basically webhooks and stuff)",
)


@api.post("/webhook/telegram/{bot_id}/{secret_key}")
async def telegram_webhook(
    request: HttpRequest,
    # Technically it's a WSGIRequest, but it's compatible with HttpRequest
    bot_id: pydantic.UUID4,
    secret_key: str,
) -> TelegramWebhookResponse:
    bot = await get_bot(
        bot_id=bot_id,
        secret_key=secret_key,
    )

    main_logger.debug(
        {
            "message": "Received Telegram webhook",
            "bot_id": bot.uuid,
            "headers": dict(request.headers),
        }
    )

    return TelegramWebhookResponse(
        status="OK",
    )
