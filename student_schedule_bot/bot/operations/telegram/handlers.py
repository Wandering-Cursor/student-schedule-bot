import urllib.parse
import uuid
from typing import TYPE_CHECKING

import pydantic
from student_schedule_bot.logger import main_logger
from telegram import Update

from bot.models.telegram.chat import TelegramChat
from bot.models.user import User
from bot.operations.schedule.read import get_photo_schedule, get_schedule, get_schedule_item
from bot.operations.telegram import messages
from bot.operations.telegram.decorators import handler_decorator
from bot.schemas.schedule.schedule import ScheduleFilters

if TYPE_CHECKING:
    from telegram.ext import ContextTypes


async def clear_keyboards(
    update: "Update",
    _context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    # TODO: Add Translations  # noqa: FIX002, TD002, TD003
    # Consider using lazy translations from Django
    await messages.clear_reply_keyboard(
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
        chat = await TelegramChat.objects.filter(
            chat_id=effective_chat.id,
        ).afirst()

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


def get_schedule_filters_from_query(callback_query: str) -> ScheduleFilters:
    filters = ScheduleFilters(page=1)

    pieces = callback_query.split("?")

    if len(pieces) == 1:
        return filters

    result = urllib.parse.parse_qs(qs="".join(pieces[1:]))

    if "page" in result:
        filters.page = int(result["page"][0])

    return filters


@handler_decorator()
async def show_schedule(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    user = await get_user(update)

    filters = None

    if update.callback_query:
        filters = get_schedule_filters_from_query(update.callback_query.data or "")

    schedule = await get_schedule(
        user=user,
        filters=filters,
    )

    await messages.show_schedule(
        update=update,
        user=user,
        schedule=schedule,
        context=context,
    )


def get_item_id_from_query(callback_query: str) -> pydantic.UUID4 | None:
    pieces = callback_query.split("?")

    if len(pieces) == 1:
        return None

    result = urllib.parse.parse_qs(qs="".join(pieces[1:]))

    if "id" in result:
        return pydantic.UUID4(result["id"][0])  # pyright: ignore[reportCallIssue]

    return None


@handler_decorator()
async def show_item(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    # Consider getting user to filter Group schedules by User's group
    if not update.callback_query:
        raise ValueError("Update does not contain a callback query.")

    item_id = get_item_id_from_query(update.callback_query.data or "")

    if not item_id:
        raise ValueError("Item ID not found in callback query.")

    item = await get_schedule_item(
        item_id=item_id,
    )

    await messages.show_item(
        update=update,
        schedule_item=item,
        context=context,
    )


def get_photo_schedule_info_from_query(
    callback_query: str,
) -> tuple[pydantic.UUID4 | None, pydantic.UUID4 | None]:
    pieces = callback_query.split("?")

    if len(pieces) == 1:
        return None, None

    result = urllib.parse.parse_qs(qs="&".join(pieces[1:]))

    photo_id = None
    item_id = None

    if "id" in result:
        photo_id = pydantic.UUID4(result["id"][0])  # pyright: ignore[reportCallIssue]

    if "item_id" in result:
        item_id = pydantic.UUID4(result["item_id"][0])  # pyright: ignore[reportCallIssue]

    return photo_id, item_id


@handler_decorator()
async def show_photo_schedule(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    if not update.callback_query:
        raise ValueError("Update does not contain a callback query.")

    photo_id, item_id = get_photo_schedule_info_from_query(update.callback_query.data or "")

    if not photo_id:
        raise ValueError("Photo Schedule ID not found in callback query.")

    photo_schedule = await get_photo_schedule(
        photo_schedule_id=photo_id,
    )

    await messages.show_photo_schedule(
        update=update,
        photo_schedule=photo_schedule,
        item_id=str(item_id) if item_id else None,
        context=context,
    )


@handler_decorator()
async def error_handler(
    update: "object",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    assert isinstance(update, Update)

    if not context.error:
        context.error = Exception("Unknown error")

    await messages.user_error_handler(
        update=update,
        error=context.error,
    )
    await messages.admin_error_handler(
        bot=context.bot,
        update=update,
        error=context.error,
    )

    main_logger.error(
        {
            "msg": "An unexpected exception arose!",
            "update": update,
            "context": context,
            "context.error": context.error,
        },
        exc_info=context.error,
    )
