import uuid
from typing import TYPE_CHECKING

from bot.models.telegram.chat import TelegramChat
from bot.models.user import User
from bot.operations.telegram import messages
from bot.operations.telegram.decorators import handler_decorator
from student_schedule_bot.logger import main_logger

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes


async def clear_keyboards(
    update: "Update",
    _context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    # TODO: Add Translations  # noqa: FIX002, TD002, TD003
    await messages.clear_keyboards(
        message="Кнопки прибрано",
        update=update,
    )


async def get_or_create_chat(
    update: "Update",
    *,
    get_only: bool = False,
) -> TelegramChat:
    if not (effective_chat := update.effective_chat):
        raise ValueError("Update does not contain an effective chat.")

    if get_only:
        chat = await TelegramChat.objects.afirst(chat_id=effective_chat.id)

        if not chat:
            raise ValueError("Chat not found.")

        return chat

    chat, created = await TelegramChat.objects.aupdate_or_create(
        chat_id=effective_chat.id,
        defaults={
            "title": effective_chat.title or f"{effective_chat.first_name} {effective_chat.last_name}",
            "username": effective_chat.username,
            "additional_info": effective_chat.to_dict(recursive=True),
        },
    )

    if created:
        main_logger.debug(
            {
                "msg": "Created new chat",
                "chat.uuid": chat.uuid,
            },
        )

    return chat


async def get_user(
    update: "Update",
    *,
    get_only: bool = False,
) -> User:
    chat = await get_or_create_chat(update, get_only=get_only)

    user, created = await User.objects.prefetch_related("telegram_chat").aget_or_create(
        username=chat.username or str(uuid.uuid4()),
        telegram_chat=chat,
    )

    if created:
        main_logger.debug(
            {
                "msg": "Created new user",
                "user.pk": user.pk,
            },
        )

    return user


@handler_decorator()
async def start(
    update: "Update",
    _context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    user = await get_user(update)

    await messages.start(
        update=update,
        user=user,
    )


@handler_decorator()
async def show_schedule(
    update: "Update",
    _context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    user = await get_user(update)

    await messages.show_schedule(
        update=update,
        user=user,
    )
