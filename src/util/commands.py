from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from src import config


async def set_commands(bot: Bot):
    await bot.delete_my_commands()
    await bot.set_my_commands(
        [BotCommand(command='/start', description='Запустить бота')],
        scope=BotCommandScopeAllPrivateChats(),
    )


async def send_bot_started_message(bot: Bot):
    await set_commands(bot)
    await bot.send_message(config.ADMIN_TG_ID, 'Бот запущен')


async def send_bot_stopped_message(bot: Bot):
    await bot.send_message(config.ADMIN_TG_ID, 'Бот остановлен')
