from typing import TYPE_CHECKING

from asgiref.sync import async_to_sync
from telegram import Bot as TelegramBot

from student_schedule_bot.logger import main_logger

if TYPE_CHECKING:
    from bot.models.telegram.bot import Bot


def set_webhook(bot: "Bot") -> bool:
    if not bot.webhook_url:
        main_logger.warning(
            {
                "msg": "Webhook URL is not set",
                "bot.uuid": bot.uuid,
            }
        )
        return False

    try:
        telegram_bot = TelegramBot(token=bot.token)
        async_to_sync(telegram_bot.set_webhook)(url=bot.full_webhook_url)
        return True
    except Exception as e:  # noqa: BLE001
        main_logger.exception(
            {
                "msg": "Failed to set webhook",
                "bot.uuid": bot.uuid,
                "error": e,
            }
        )
        return False
