import logging
import uuid
from typing import Dict, Optional

from aiogram import types
from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import AsyncSession

import src.keyboard.message as messages
from lib.asyncxui.config_gen import config_generator
from lib.asyncxui.xui import XUI
from src.config import CHAT_TG_ID
from src.db.adapter.server import (
    decrement_available_subs,
    get_server_with_most_available_subs,
)
from src.db.adapter.sub import (
    add_sub,
    delete_subs,
    is_active_sub,
)
from src.db.entity import Server, User
from src.keyboard import main_menu_kb
from src.util.panel import Panel
from src.util.vpn import generate_email


async def create_sub(
    session: AsyncSession,
    user: User,
    message: types.Message,
):
    # Получение сервера
    server: Optional[Server] = await get_server_with_most_available_subs(session)

    if not server:
        await message.answer(messages.NoAvailableServers, reply_markup=main_menu_kb)
        return

    try:
        # Инициализация доступа к панели
        panel: XUI = await Panel().init(server)
    except Exception as e:
        logging.debug(f'Ошибка при инициализации доступа к панели: {e}')
        await message.answer(
            'Что то случилось с сервером. Видимо опять траншею копают.'
        )
        return

    # Генерация данных
    user_uuid = str(uuid.uuid4())
    user_email = generate_email(user.telegram_id, user.username)

    # Обновление базы данных
    sub_id: int = await add_sub(
        session,
        user_id=user.user_id,
        server_id=server.server_id,
        user_uuid=user_uuid,
        user_email=user_email,
        ip_limit=2,
    )

    logging.debug(f'Нагрузка пользователя: {user.load_weight}')
    await decrement_available_subs(session, server.server_id, user.load_weight)

    # Добавление клиента в панель
    await panel.add_client(
        inbound_id=1,
        email=user_email,
        uuid=user_uuid,
        enable=True,
        flow='xtls-rprx-vision',
        limit_ip=2,
        telegram_id=str(user.telegram_id),
        subscription_id=str(sub_id),
    )

    # Генерация ссылки
    config: Dict[str, str] = {
        'uuid': user_uuid,
        'server_ip': server.server_ip,
        'email': user_email,
    }
    link = config_generator(config, server.query_params)

    # Ответ пользователю
    await message.answer(
        messages.generate_link_message(link),
        parse_mode='HTML',
        reply_markup=main_menu_kb,
    )


async def check_and_delete_sub(
    session: AsyncSession,
    limiter: AsyncLimiter,
    user: User,
    message: types.Message,
):
    async with limiter:
        try:
            if message.bot is None:
                raise Exception('Бот недоступен')
            chat_member = await message.bot.get_chat_member(
                str(CHAT_TG_ID), user.telegram_id
            )
            if chat_member.status not in ('member', 'creator', 'administrator'):
                logging.debug(f'{user.username} не имеет доступа к боту')
                if not await is_active_sub(session, user.user_id):
                    logging.debug(f'{user.username} не имеет активной подписки')
                    return
                logging.debug(f'Удаление подписки для пользователя {user.telegram_id}')
                await delete_subs(session, user.telegram_id)
                await message.bot.send_message(
                    user.telegram_id,
                    'Ваш VPN был отключен, тк вы отписались от подписки :(. Подпишитесь снова!',
                )

                await message.answer(
                    f'Удалена подписка для пользователя @{user.username} (ID: {user.telegram_id})'
                )

        except Exception as e:
            logging.debug(
                f'Ошибка при проверке пользователя {user.username} (ID: {user.telegram_id}): {e}'
            )
