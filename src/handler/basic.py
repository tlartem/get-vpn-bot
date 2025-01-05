from aiogram import F, Router, types
from aiogram.filters import Command

from config import ADMIN_TG_USERNAME
from src.db.adapter.user import add_user, get_user
from src.db.postgres import get_session
from src.keyboard import main_menu_kb

basic_router = Router()
basic_router.message.filter(F.chat.type == 'private')


@basic_router.message(Command('start'))
async def cmd_start(message: types.Message):
    if message.from_user is None:
        await message.answer('Внутренняя ошибка бота')
        return

    async with get_session() as session:
        if not await get_user(session, message.from_user.id):
            await add_user(session, message.from_user.id, message.from_user.username)

    await message.answer(
        'Кнопочку нажми, чтобы получить VPN',
        reply_markup=main_menu_kb,
    )


@basic_router.message(F.text == 'Поддержка')
async def support(message: types.Message):
    await message.answer(f'Свяжитесь с поддержкой в Telegram: @{ADMIN_TG_USERNAME}')
