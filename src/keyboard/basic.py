from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.config import VPN_USAGE_WEIGHTS, YOUTUBE_USAGE_WEIGHT

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Получить VPN'),
            KeyboardButton(text='Поддержка'),
        ]
    ],
)

how_often_use_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=button_name) for button_name in VPN_USAGE_WEIGHTS.keys()]
    ],
)
does_youtube_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=button_name)
            for button_name in YOUTUBE_USAGE_WEIGHT.keys()
        ]
    ],
)
