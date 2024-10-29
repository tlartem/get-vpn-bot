import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

import config
from handlers.basic import cmd_start, get_vpn, support
from utils.commands import send_bot_started_message, send_bot_stopped_message


async def main():
    logging.basicConfig(
        level=logging.DEBUG,  # Изменил уровень логирования для отладки
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()
    dp.startup.register(send_bot_started_message)
    dp.shutdown.register(send_bot_stopped_message)

    dp.message.register(cmd_start, Command('start'))
    dp.message.register(get_vpn, F.text == 'Получить VPN')
    dp.message.register(support, F.text == 'Поддержка')

    try:
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(e)

    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
