from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сохранить профиль", callback_data="save_profile"),
                InlineKeyboardButton(text="Напомнить уход", callback_data="set_reminder"),
            ],
            [
                InlineKeyboardButton(text="Политика и условия", callback_data="show_terms"),
            ],
        ]
    )

