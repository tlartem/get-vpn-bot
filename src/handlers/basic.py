from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import CHAT_TG_ID
from repository import add_user, get_user_id_by_telegram_id, is_active_sub
from services.vpn import create_sub


async def cmd_start(message: types.Message):
    if not await get_user_id_by_telegram_id(message.from_user.id):
        await add_user(message.from_user.id, message.from_user.username)

    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Получить VPN'),
                KeyboardButton(text='Поддержка'),
            ]
        ],
    )

    await message.answer(
        'Кнопочку нажми, чтобы получить VPN',
        reply_markup=reply_keyboard,
    )


async def get_vpn(message: types.Message):
    if await is_active_sub(await get_user_id_by_telegram_id(message.from_user.id)):
        await message.answer('У тебя уже есть активная подписка')
        return

    if not await get_user_id_by_telegram_id(message.from_user.id):
        await message.answer('Произошла ошибка при получении твоего ID')
        return

    try:
        user_member = await message.bot.get_chat_member(
            CHAT_TG_ID, message.from_user.id
        )
        if user_member.status not in ('member', 'creator', 'administrator'):
            await message.answer(
                'Ты должен быть участником чата, чтобы получить подписку.'
            )
            return
    except Exception:
        await message.answer('Ты должен быть участником чата, чтобы получить подписку.')
        return

    await create_sub(message.from_user.id, message.from_user.username, message)


async def support(message: types.Message):
    await message.answer('Свяжитесь с поддержкой в Telegram: @temiso')
