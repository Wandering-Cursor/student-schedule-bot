from typing import TYPE_CHECKING

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from bot.operations.telegram.enums import Commands
from student_schedule_bot.config import config

if TYPE_CHECKING:
    from telegram import Update
    from telegram._utils.types import ReplyMarkup

    from bot.models.user import User
    from bot.schemas.schedule.schedule import ScheduleResponse


async def clear_keyboards(
    message: str,
    update: "Update",
) -> None:
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove(),
    )


async def reply_or_edit(
    update: "Update",
    text: str,
    markup: "ReplyMarkup | None" = None,
) -> None:
    if update.effective_message.from_user.is_bot:
        await update.effective_message.edit_text(
            text,
            reply_markup=markup,
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=markup,
        )


async def start(
    update: "Update",
    user: "User",
) -> None:
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📅 Розклад", callback_data=Commands.SHOW_SCHEDULE),
            ],
        ]
    )

    await reply_or_edit(
        update,
        text=f"{user.telegram_chat.title}, вітаємо у боті ФКПАІТ ОНТУ!",
        markup=markup,
    )


async def show_schedule(
    update: "Update",
    user: "User",
    schedule: "ScheduleResponse",
) -> None:
    keyboard = []

    for item in schedule.results:
        photo_icon = "🖼️ "
        group_icon = "👥 "

        group = group_icon if item.group_schedules else ""
        photo = photo_icon if item.photo_schedule else ""

        name = f"{group}{photo}{item.for_date}"

        keyboard.append(
            [
                InlineKeyboardButton(
                    name,
                    callback_data=Commands.show_item(item_id=str(item.uuid)),
                ),
            ]
        )

    control_row = []

    # In case we add pagination counters using inserts
    if schedule.previous:
        control_row.insert(
            0,
            InlineKeyboardButton(
                "⬅️ Попередня Сторінка",
                callback_data=Commands.schedule_page(schedule.previous_page_number),
            ),
        )  # type: ignore
    if schedule.next:
        control_row.append(
            InlineKeyboardButton(
                "➡️ Наступна Сторінка",
                callback_data=Commands.schedule_page(schedule.next_page_number),
            )
        )  # type: ignore

    keyboard.append(control_row)

    keyboard.append([InlineKeyboardButton("🏠 До Головного Меню", callback_data=Commands.SHOW_MAIN_MENU)])

    markup = InlineKeyboardMarkup(keyboard)

    await reply_or_edit(
        update,
        text=f"Розклад ({schedule.count}):",
        markup=markup,
    )


async def user_error_handler(
    update: "Update",
    error: Exception,
) -> None:
    arguments = [
        ("update.update_id", update.update_id),
        ("update.effective_chat.id", update.effective_chat.id if update.effective_chat else None),
        ("type(error)", type(error)),
    ]
    error_info = "\n".join(f"{key}: {value}" for key, value in arguments)
    message_text = f"Вибачте, сталася помилка.\nВи можете надати наступну інформацію:\n```\n{error_info}\n```"

    await update.effective_message.reply_text(
        message_text.replace(".", "\\."),
        parse_mode="MarkdownV2",
    )


async def admin_error_handler(
    bot: "Bot",
    update: "Update",
    error: Exception,
) -> None:
    admin_chat_id = config.ADMIN_CHAT_ID

    if admin_chat_id is None:
        return

    arguments = [
        ("update.update_id", update.update_id),
        ("update.effective_chat.id", update.effective_chat.id if update.effective_chat else None),
        ("error", repr(error)),
    ]
    error_info = "\n".join(f"{key}: {value}" for key, value in arguments)
    message_text = f"Помилка в користувача:\n\n```\n{error_info}\n```"

    await bot.send_message(
        chat_id=admin_chat_id,
        text=message_text,
        parse_mode="MarkdownV2",
    )
