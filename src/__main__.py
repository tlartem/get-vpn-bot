import asyncio
import logging

from aiogram import Bot, Dispatcher

from src import config
from src.db.postgres import init_db
from src.handler.basic import basic_router
from src.handler.get_vpn import vpn_router
from src.util.commands import send_bot_started_message, send_bot_stopped_message


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    await init_db()

    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(basic_router)
    dp.include_router(vpn_router)

    if not config.IS_DEBUG:
        dp.startup.register(send_bot_started_message)
        dp.shutdown.register(send_bot_stopped_message)

    try:
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(e)

    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
