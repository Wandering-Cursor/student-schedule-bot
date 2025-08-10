from typing import TYPE_CHECKING

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

if TYPE_CHECKING:
    from telegram import Update

    from bot.models.user import User


async def clear_keyboards(
    message: str,
    update: "Update",
) -> None:
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove(),
    )


async def start(
    update: "Update",
    user: "User",
) -> None:
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📅 Розклад", callback_data="get_schedule"),
            ],
        ]
    )

    await update.message.reply_text(
        f"{user.telegram_chat.title}, вітаємо у боті ФКПАІТ ОНТУ!",
        reply_markup=markup,
    )
