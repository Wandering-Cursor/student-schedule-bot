import pydantic

from bot.errors.http import AuthorizationError
from bot.models.telegram.bot import Bot


async def get_bot(
    bot_id: pydantic.UUID4,
    secret_key: str,
) -> Bot:
    bot = await Bot.objects.filter(
        uuid=bot_id,
    ).afirst()

    if not bot:
        raise AuthorizationError(
            log_message={
                "msg": "Bot not found",
                "bot_id": bot_id,
            }
        )

    if bot.secret_key != secret_key:
        raise AuthorizationError(
            log_message={
                "msg": "Invalid secret key",
                "bot_id": bot_id,
                "provided_secret_key": secret_key,
            }
        )

    return bot
