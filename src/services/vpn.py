import uuid

from aiogram import types

from asyncxui import XUI
from asyncxui.config_gen import config_generator
from config import INSTRUCTION_LINK
from repository import (
    add_subscription,
    change_sub_status,
    decrement_available_subs,
    get_server_by_id,
    get_server_with_most_available_subs,
    get_sub_id_by_telegram_id,
    get_sub_server_id_by_telegram_id,
    get_user_id_by_telegram_id,
    get_user_uuid_by_telegram_id,
)
from utils.vpn import generate_email


async def create_sub(tg_user_id: int, tg_username: str, message: types.Message):
    server = await get_server_with_most_available_subs()
    if not server:
        await message.answer('В данный момент нет доступных серверов')
        return

    panel = XUI(full_address=server.host, panel='sanaei')

    await panel.login(server.login, server.password)

    user_uuid = str(uuid.uuid4())
    user_email = generate_email(tg_user_id)

    sub_id = await add_subscription(
        user_id=await get_user_id_by_telegram_id(tg_user_id),
        server_id=server.server_id,
        user_uuid=user_uuid,
        user_email=user_email,
        ip_limit=2,
    )

    await decrement_available_subs(server.server_id)

    await panel.add_client(
        inbound_id=1,
        email=user_email,
        uuid=user_uuid,
        enable=True,
        flow='xtls-rprx-vision',
        limit_ip=2,
        telegram_id=tg_username,
        subscription_id=sub_id,
    )

    config = dict(uuid=user_uuid, server_ip=server.server_ip, email=user_email)
    link = config_generator(config, server.query_params)

    await message.answer(
        f'<code>{link}</code>\n\n'
        f'<b>(Ссылка кликабельная)</b>\n'
        f'Как поставить?: <a href="{INSTRUCTION_LINK}">ссылка</a>',
        parse_mode='HTML',
    )


async def delete_sub(telegram_id: int):
    server = await get_server_by_id(await get_sub_server_id_by_telegram_id(telegram_id))
    print(server)
    user_uuid = await get_user_uuid_by_telegram_id(telegram_id)
    print(user_uuid)
    panel = XUI(full_address=server.host, panel='sanaei')

    await panel.login(server.login, server.password)
    print(1)
    await panel.delete_client(1, uuid=user_uuid)
    print(2)
    sub_id = await get_sub_id_by_telegram_id(telegram_id)
    print(3)
    await change_sub_status(sub_id, False)
    print(4)
