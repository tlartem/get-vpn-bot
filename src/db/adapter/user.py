from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.entity import Subscription, User


async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    return user


async def add_user(
    session: AsyncSession, telegram_id: int, username: str | None, admin: bool = False
) -> None:
    new_user = User(telegram_id=telegram_id, username=username, admin=admin)
    session.add(new_user)
    await session.commit()


async def delete_user(session: AsyncSession, telegram_id: int) -> None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user: Optional[User] = result.scalar_one_or_none()
    if user:
        await session.delete(user)
        await session.commit()


async def user_set_weight(
    session: AsyncSession, user_id: int, weight: float
) -> User | None:
    user: User | None = await session.get(User, user_id)
    if user:
        user.load_weight = weight
        await session.commit()
    return user


async def get_user_uuid_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> Optional[str]:
    result = await session.execute(
        select(Subscription.user_uuid)
        .join(User)
        .where(User.telegram_id == telegram_id, Subscription.status == True)
    )
    user_uuid: Optional[str] = result.scalar_one_or_none()
    return user_uuid
