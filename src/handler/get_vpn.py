import asyncio
import json

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiolimiter import AsyncLimiter
from sqlalchemy import select

from src.config import ADMIN_TG_ID, CHAT_TG_ID, VPN_USAGE_WEIGHTS, YOUTUBE_USAGE_WEIGHT
from src.db.adapter.server import add_server
from src.db.adapter.sub import is_active_sub
from src.db.adapter.user import get_user, user_set_weight
from src.db.entity import User
from src.db.postgres import get_session
from src.keyboard import does_youtube_kb, how_often_use_kb, main_menu_kb
from src.usecase.vpn import check_and_delete_sub, create_sub
from src.util.panel import Panel
from src.util.state import AddServerStates, Form

vpn_router = Router()
vpn_router.message.filter(F.chat.type == 'private')


@vpn_router.message(F.text == 'Получить VPN')
async def get_vpn(message: types.Message, state: FSMContext) -> None:
    if not message.from_user or not message.bot or not CHAT_TG_ID:
        print('Внутренняя ошибка бота')
        return

    async with get_session() as session:
        # Проверки валидности
        user: User | None = await get_user(session, message.from_user.id)

        if not user:
            await message.answer(
                'Ты не зарегистрирован в системе',
                reply_markup=main_menu_kb,
            )
            return

        if await is_active_sub(session, user.user_id):
            await message.answer(
                'У тебя уже есть активная подписка',
                reply_markup=main_menu_kb,
            )
            return

        chat_member = await message.bot.get_chat_member(CHAT_TG_ID, user.telegram_id)

        if chat_member.status not in ('member', 'creator', 'administrator'):
            await message.answer(
                'Ты должен быть участником чата, чтобы получить подписку.',
                reply_markup=main_menu_kb,
            )
            return

    # Алгоритм создания
    await state.set_state(Form.how_often_use)
    await state.update_data(user=user)
    await message.answer(
        'Как часто ты планируешь использовать VPN?', reply_markup=how_often_use_kb
    )


@vpn_router.message(Form.how_often_use)
async def process_how_often_use(message: types.Message, state: FSMContext) -> None:
    frequency = message.text

    if frequency not in VPN_USAGE_WEIGHTS.keys():
        await message.answer(
            'Пожалуйста, выбери один из вариантов.', reply_markup=how_often_use_kb
        )
        return

    await state.update_data(user_weight=VPN_USAGE_WEIGHTS[frequency])
    await state.set_state(Form.does_youtube_use)

    await message.answer(
        'Будешь постоянно смотреть YouTube на VPN?',
        reply_markup=does_youtube_kb,
    )


@vpn_router.message(Form.does_youtube_use)
async def process_does_youtube_use(message: types.Message, state: FSMContext) -> None:
    youtube = message.text

    if youtube not in YOUTUBE_USAGE_WEIGHT.keys():
        await message.answer(
            'Пожалуйста, выбери один из вариантов.',
            reply_markup=does_youtube_kb,
        )
        return

    async with get_session() as session:
        data: dict = await state.get_data()
        user_weight: float = data['user_weight']
        user_weight += YOUTUBE_USAGE_WEIGHT[youtube]

        user: User = data['user']
        user = await user_set_weight(session, user.user_id, user_weight)

        await create_sub(session, user, message)

    await state.clear()


@vpn_router.message(F.text == 'Добавить сервер')
async def cmd_add_server(message: types.Message, state: FSMContext):
    if message.from_user is None or message.from_user.id != ADMIN_TG_ID:
        await message.reply('У вас нет прав для выполнения этой команды.')
        return
    await message.reply(
        'Пожалуйста, отправьте данные сервера в формате JSON.\n'
        'Пример:\n'
        '{\n'
        '  "host": "example.com",\n'
        '  "login": "admin",\n'
        '  "password": "secret",\n'
        '  "country": "USA",\n'
        '  "query_params": "param1,param2",\n'
        '  "server_available_load": 50.0,\n'
        '  "server_ip": "192.168.1.1"\n'
        '}'
    )
    await state.set_state(AddServerStates.waiting_for_json)


@vpn_router.message(AddServerStates.waiting_for_json)
async def check_server(message: types.Message, state: FSMContext):
    if message.text is None:
        return
    json_text = message.text.strip()
    try:
        server_data = json.loads(json_text)
    except json.JSONDecodeError:
        await message.reply(
            'Неверный формат JSON. Пожалуйста, убедитесь, что ваш JSON корректен.'
        )
        return
    await state.set_state(AddServerStates.waiting_for_json)

    # Проверка наличия всех необходимых полей
    required_fields = [
        'host',
        'login',
        'password',
        'country',
        'query_params',
        'server_available_load',
        'server_ip',
    ]
    missing_fields = [field for field in required_fields if field not in server_data]
    if missing_fields:
        await message.reply(
            f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        )
        return

    host = server_data['host'].strip()
    login = server_data['login'].strip()
    password = server_data['password'].strip()
    country = server_data['country'].strip()
    query_params = server_data['query_params'].strip()
    server_ip = server_data['server_ip'].strip()
    server_available_load = server_data['server_available_load']

    # Проверка подключения к серверу
    await message.reply('Проверка подключения к серверу...')
    connection_success = await Panel().check_login(host, login, password)
    if not connection_success:
        await message.reply(
            'Не удалось подключиться к серверу. Пожалуйста, проверьте данные и попробуйте снова.'
        )
        return

    async with get_session() as session:
        try:
            new_server = await add_server(
                session=session,
                host=host,
                login=login,
                password=password,
                country=country,
                server_available_load=server_available_load,
                query_params=query_params,
                server_ip=server_ip,
            )
            await message.reply(
                f'Сервер добавлен успешно! ID сервера: {new_server.server_id}'
            )
        except Exception as e:
            await message.reply(f'Произошла ошибка при добавлении сервера: {e}')
        finally:
            await state.clear()
    await state.clear()


@vpn_router.message(F.text == 'Очистка')
async def remove_non_chat_members(message: types.Message):
    limiter = AsyncLimiter(max_rate=5, time_period=1)

    if message.from_user is None or message.from_user.id != ADMIN_TG_ID:
        await message.reply('У вас нет прав для выполнения этой команды.')
        return

    async with get_session() as session:
        offset = 0
        while True:
            result = await session.execute(select(User).offset(offset).limit(10))
            users = result.scalars().all()
            if not users:
                break  # Все пользователи обработаны

            tasks = [
                check_and_delete_sub(session, limiter, user, message) for user in users
            ]
            await asyncio.gather(*tasks)
            offset += 10
