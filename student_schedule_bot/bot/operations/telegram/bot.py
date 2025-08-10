from functools import lru_cache
from typing import TYPE_CHECKING

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.operations.telegram import handlers
from bot.operations.telegram.enums import ApplicationStates, Commands

if TYPE_CHECKING:
    from bot.models.telegram.bot import Bot as BotModel


async def get_bot(bot_instance: "BotModel") -> "Application":
    application = Application.builder().token(bot_instance.token).build()

    application.add_handler(
        CommandHandler(
            "start",
            handlers.start,
        )
    )

    application.add_handler(
        CommandHandler(
            "clear_keyboard",
            handlers.clear_keyboards,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handlers.show_schedule,
            pattern=Commands.SHOW_SCHEDULE.as_regex,
        )
    )

    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.to_start,
    #         pattern=Commands.TO_START.as_regex,
    #     )
    # )
    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.show_balances,
    #         pattern=Commands.BALANCES.as_regex,
    #     ),
    # )
    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.show_settings,
    #         pattern=Commands.SETTINGS.as_regex,
    #     ),
    # )
    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.show_tasks,
    #         pattern=Commands.TASKS.as_regex,
    #     ),
    # )

    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.show_tasks_pages,
    #         pattern=Commands.AVAILABLE_TASKS.as_regex,
    #     ),
    # )
    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.show_tasks_pages,
    #         pattern=Commands.COMPLETED_TASKS.as_regex,
    #     ),
    # )

    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.update_event,
    #         pattern=Commands.CHANGE_EVENT.as_regex,
    #     )
    # )
    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.set_event,
    #         pattern=Commands.CHANGE_EVENT_CONFIRMATION.as_regex,
    #     )
    # )

    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.toggle_publicity,
    #         pattern=Commands.TOGGLE_PUBLICITY.as_regex,
    #     )
    # )

    # application.add_handler(
    #     CallbackQueryHandler(
    #         handlers.remove_account,
    #         pattern=Commands.REMOVE_ACCOUNT.as_regex,
    #     )
    # )

    await application.initialize()

    return application


async def process_webhook_with_bot(bot_instance: "BotModel", update_data: dict) -> None:
    application = await get_bot(bot_instance)

    update = Update.de_json(update_data, bot=application.bot)

    await application.process_update(update)

    await application.shutdown()
