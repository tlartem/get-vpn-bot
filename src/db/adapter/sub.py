import asyncio
import logging
from datetime import datetime
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from lib.asyncxui.xui import XUI
from src.db.adapter.user import get_user
from src.db.entity import Server, Subscription, User


async def add_sub(
    session: AsyncSession,
    user_id: int,
    server_id: int,
    user_uuid: str,
    user_email: str,
    ip_limit: int,
) -> int:
    new_sub = Subscription(
        user_id=user_id,
        server_id=server_id,
        user_uuid=user_uuid,
        user_email=user_email,
        ip_limit=ip_limit,
    )
    session.add(new_sub)
    await session.commit()
    await session.refresh(new_sub)
    return new_sub.sub_id


async def change_sub_status(session: AsyncSession, sub_id: int, status: bool) -> None:
    stmt = (
        update(Subscription)
        .where(Subscription.sub_id == sub_id)
        .values(status=status, end_date=None if status else datetime.now())
    )
    await session.execute(stmt)
    await session.commit()


async def is_active_sub(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(
        select(Subscription.status).where(Subscription.user_id == user_id)
    )
    statuses = result.scalars().all()
    return any(status for status in statuses)


async def get_user_subscriptions(
    session: AsyncSession, user_id: int
) -> List[Subscription]:
    try:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == True)
        )
        subscriptions = result.scalars().all()
        logging.debug(
            f'Найдено {len(subscriptions)} подписок для пользователя с ID {user_id}.'
        )
        return list(subscriptions)
    except Exception as e:
        logging.error(
            f'Ошибка при получении подписок для пользователя с ID {user_id}: {e}'
        )
        return []


async def get_server_by_subscription(
    session: AsyncSession, sub_id: int
) -> Server | None:
    try:
        result = await session.execute(
            select(Server)
            .join(Subscription, Server.server_id == Subscription.server_id)
            .where(Subscription.sub_id == sub_id)
        )
        server = result.scalars().first()

        if not server:
            logging.debug(f'Сервер для подписки с ID {sub_id} не найден.')
            return None

        logging.debug(f'Сервер найден: {server.host} для подписки ID {sub_id}.')
        return server

    except Exception as e:
        logging.error(f'Ошибка при получении сервера для подписки с ID {sub_id}: {e}')
        return None


async def delete_subs(session: AsyncSession, telegram_id: int):
    user: User | None = await get_user(session, telegram_id)

    if not user:
        logging.debug('Пользователь не найден')
        return

    logging.debug(f'Получение {user.username} subscriptions')
    subscriptions: List[Subscription] = await get_user_subscriptions(
        session, user.user_id
    )

    logging.debug(f'У {user.username} есть {len(subscriptions)} активных подписок')

    if not subscriptions:
        logging.debug(f'У {user.username} нет активных подписок')
        return

    # Удаляем все подписки
    for subscription in subscriptions:
        logging.debug(f'Удаляем подписку {subscription.sub_id}')
        server: Server | None = await get_server_by_subscription(
            session, subscription.sub_id
        )

        if not server:
            continue

        await asyncio.sleep(2)

        panel = XUI(full_address=server.host, panel='sanaei')
        await panel.login(server.login, server.password)
        await panel.delete_client(1, uuid=subscription.user_uuid)

        subscription.status = False
        subscription.end_date = datetime.now()

        server.server_available_load += user.load_weight

    await session.commit()
    logging.debug(f'Все подписки {user.telegram_id} успешно удалены.')
