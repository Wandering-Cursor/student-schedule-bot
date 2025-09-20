from typing import TYPE_CHECKING

from student_schedule_bot.config import config
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardRemove

from bot.models.telegram.chat import TelegramChat
from bot.operations.telegram.enums import Commands

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

    from bot.models.user import User
    from bot.schemas.schedule.schedule import PhotoSchedule, Schedule, ScheduleResponse


async def clear_reply_keyboard(
    message: str,
    update: "Update",
) -> None:
    assert update.message is not None

    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove(),
    )


async def reply_or_edit(
    update: "Update",
    text: str,
    markup: "InlineKeyboardMarkup | None" = None,
    context: "ContextTypes.DEFAULT_TYPE | None" = None,
) -> None:
    assert update.effective_message is not None

    effective_message = update.effective_message

    assert effective_message.from_user is not None

    if effective_message.from_user.is_bot:
        reply_to = effective_message.reply_to_message
        if reply_to and reply_to.media_group_id:
            media_group_id = reply_to.media_group_id
            if context and context.chat_data:
                group_messages = context.chat_data.get("media_groups", {}).get(media_group_id, [])
                await update.get_bot().delete_messages(
                    chat_id=effective_message.chat_id,
                    message_ids=group_messages,
                )
        if effective_message.text:
            await effective_message.edit_text(
                text,
                reply_markup=markup,
            )
        else:
            await update.effective_message.delete()

            assert update.effective_chat is not None

            await update.effective_chat.send_message(
                text,
                reply_markup=markup,
            )
    else:
        assert update.message is not None

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

    if user.telegram_chat is None:
        user.telegram_chat = TelegramChat(
            title="Unknown Chat",
        )

    await reply_or_edit(
        update,
        text=f"{user.telegram_chat.title}, вітаємо у боті ФКПАІТ ОНТУ!",
        markup=markup,
    )


async def show_schedule(
    update: "Update",
    user: "User",  # Consider using User entity to show group schedule  # noqa: ARG001
    schedule: "ScheduleResponse",
    context: "ContextTypes.DEFAULT_TYPE | None" = None,
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
    if previous := schedule.previous_page_number:
        control_row.insert(
            0,
            InlineKeyboardButton(
                "⬅️ Попередня Сторінка",
                callback_data=Commands.schedule_page(previous),
            ),
        )
    if next_number := schedule.next_page_number:
        control_row.append(
            InlineKeyboardButton(
                "➡️ Наступна Сторінка",
                callback_data=Commands.schedule_page(next_number),
            )
        )

    keyboard.append(control_row)

    keyboard.append([InlineKeyboardButton("🏠 До Головного Меню", callback_data=Commands.SHOW_MAIN_MENU)])

    markup = InlineKeyboardMarkup(keyboard)

    await reply_or_edit(
        update,
        text=f"Розклад ({schedule.count}):",
        markup=markup,
        context=context,
    )


async def show_item(
    update: "Update",
    schedule_item: "Schedule",
    context: "ContextTypes.DEFAULT_TYPE | None" = None,
) -> None:
    # NOTE: Not handling group schedules yet
    group_schedule = "❌" if not schedule_item.group_schedules else "✅"
    photo_schedule = "❌" if not schedule_item.photo_schedule else "✅"

    schedule_description = f"Розклад на {schedule_item.for_date}:"
    group_schedule_notice = f"Розклад для груп: {group_schedule}"
    photo_schedule_notice = f"Розклад у вигляді фото: {photo_schedule}"
    updated_at = f"Оновлено о: {schedule_item.updated_at.strftime('%Y-%m-%d %H:%M')}"

    text = f"{schedule_description}\n\n{group_schedule_notice}\n{photo_schedule_notice}\n\n{updated_at}"

    keyboard = []

    if photo_schedule_id := schedule_item.photo_schedule_id:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "🖼️ Переглянути Фото Розкладу",
                    callback_data=Commands.show_photo_schedule(
                        photo_id=str(photo_schedule_id),
                        item_id=str(schedule_item.uuid),
                    ),
                ),
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton("📅 До Розкладу", callback_data=Commands.SHOW_SCHEDULE),
        ],
    )

    await reply_or_edit(
        update=update,
        text=text,
        markup=InlineKeyboardMarkup(keyboard),
        context=context,
    )


async def show_photo_schedule(
    update: "Update",
    photo_schedule: "PhotoSchedule",
    item_id: str | None = None,
    context: "ContextTypes.DEFAULT_TYPE | None" = None,
) -> None:
    keyboard = []

    if item_id:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "📄 До розкладу на день",
                    callback_data=Commands.show_item(item_id=item_id),
                ),
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton("📅 До Розкладу", callback_data=Commands.SHOW_SCHEDULE),
        ],
    )

    assert update.effective_message is not None

    messages = await update.effective_message.reply_media_group(
        media=[
            InputMediaPhoto(
                media=str(photo.file),
            )
            for photo in photo_schedule.photos
        ],
        caption=f"Фото розкладу:\n\nОпис: {photo_schedule.name or 'Без назви'}\nОновлено о: {photo_schedule.updated_at.strftime('%Y-%m-%d %H:%M')}",
    )

    first = messages[0]
    if len(messages) == 1:
        await first.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await first.reply_text(
            "Використовуйте кнопки для навігації",
            reply_markup=InlineKeyboardMarkup(keyboard),
            reply_to_message_id=first.message_id,
        )

    # For removing >1 message
    if context and context.chat_data is not None:
        media_groups = context.chat_data.get("media_groups", {})
        media_groups[first.media_group_id] = [msg.message_id for msg in messages]
        context.chat_data["media_groups"] = media_groups

    await update.effective_message.delete()


async def user_error_handler(
    update: "Update",
    error: Exception,
) -> None:
    assert update.effective_message is not None

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
