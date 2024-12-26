from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.entity import Server, Subscription, User


async def get_server_with_most_available_subs(
    session: AsyncSession,
) -> Optional[Server]:
    result = await session.execute(
        select(Server)
        .where(Server.server_available_load > 0)
        .order_by(Server.server_available_load.desc())
        .limit(1)
    )

    server = result.scalar_one_or_none()

    return server


async def increment_available_subs(
    session: AsyncSession, server_id: int, times: float
) -> None:
    stmt = (
        update(Server)
        .where(Server.server_id == server_id)
        .values(server_available_load=Server.server_available_load + times)
    )
    await session.execute(stmt)
    await session.commit()


async def decrement_available_subs(
    session: AsyncSession, server_id: int, times: float
) -> None:
    stmt = (
        update(Server)
        .where(Server.server_id == server_id)
        .values(server_available_load=Server.server_available_load - times)
    )
    await session.execute(stmt)
    await session.commit()


async def add_server(
    session: AsyncSession,
    host: str,
    login: str,
    password: str,
    country: str,
    query_params: str,
    server_available_load: float,
    server_ip: str,
) -> Server:
    new_server = Server(
        host=host,
        login=login,
        password=password,
        country=country,
        server_available_load=server_available_load,
        query_params=query_params,
        server_ip=server_ip,
    )
    session.add(new_server)
    await session.commit()
    await session.refresh(new_server)
    return new_server


async def get_users_with_active_subs(session: AsyncSession) -> List[int]:
    result: Result = await session.execute(
        select(User.telegram_id).join(Subscription).where(Subscription.status == True)
    )
    return list(result.scalars().all())


async def get_sub_server_id_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> Optional[int]:
    result = await session.execute(
        select(Subscription.server_id)
        .join(User)
        .where(User.telegram_id == telegram_id, Subscription.status == True)
    )
    server_id = result.scalar_one_or_none()
    return server_id
