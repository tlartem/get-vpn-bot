import asyncio
from dataclasses import dataclass

import asyncpg

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


async def get_connection():
    return await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
    )


async def create_tables():
    conn = await get_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(255),
            admin BOOLEAN DEFAULT FALSE
        );
        """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            server_id SERIAL PRIMARY KEY,
            host VARCHAR(255),
            login VARCHAR(255),
            password VARCHAR(255),
            country VARCHAR(255),
            available_subs INTEGER DEFAULT 0,
            query_params VARCHAR(255),
            server_ip VARCHAR(255)
        );
        """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            sub_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            server_id INTEGER REFERENCES servers(server_id),
            user_uuid VARCHAR(255),
            user_email VARCHAR(255),
            ip_limit INTEGER,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP DEFAULT NULL,
            status BOOLEAN DEFAULT TRUE
        )
        """)

    await conn.close()


async def add_user(telegram_id: int, username: str, admin: bool = False):
    conn = await get_connection()
    await conn.execute(
        """
        INSERT INTO users (telegram_id, username, admin) VALUES ($1, $2, $3)
    """,
        telegram_id,
        username,
        admin,
    )
    await conn.close()


async def delete_user(telegram_id: int):
    conn = await get_connection()
    await conn.execute(
        """
        DELETE FROM users WHERE telegram_id = $1
    """,
        telegram_id,
    )
    await conn.close()


async def add_subscription(
    user_id: int, server_id: int, user_uuid: str, user_email: str, ip_limit: int
) -> int:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        INSERT INTO subscriptions (user_id, server_id, user_uuid, user_email, ip_limit) 
        VALUES ($1, $2, $3, $4, $5) RETURNING sub_id
    """,
        user_id,
        server_id,
        user_uuid,
        user_email,
        ip_limit,
    )
    await conn.close()
    return result['sub_id'] if result else None


async def change_sub_status(sub_id: int, status: bool):
    conn = await get_connection()
    await conn.execute(
        """
        UPDATE subscriptions SET status = $1, end_date = $2 WHERE sub_id = $3
    """,
        status,
        None if status else 'NOW()',
        sub_id,
    )
    await conn.close()


async def is_active_sub(user_id: int) -> bool:
    conn = await get_connection()
    results = await conn.fetch(
        """
        SELECT status FROM subscriptions 
        WHERE user_id = $1
        """,
        user_id,
    )
    await conn.close()
    return any(result['status'] for result in results) if results else False


async def get_user_id_by_telegram_id(telegram_id: int) -> int:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT user_id FROM users WHERE telegram_id = $1
        """,
        telegram_id,
    )
    await conn.close()
    return result['user_id'] if result else None


async def get_user_uuid_by_telegram_id(telegram_id: int) -> str:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT s.user_uuid FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE u.telegram_id = $1 AND s.status = TRUE
        """,
        telegram_id,
    )
    await conn.close()
    return result['user_uuid'] if result else None


async def get_sub_id_by_telegram_id(telegram_id: int) -> int:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT s.sub_id FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE u.telegram_id = $1 AND s.status = TRUE
        """,
        telegram_id,
    )
    await conn.close()
    return result['sub_id'] if result else None


@dataclass
class Server:
    server_id: int
    host: str
    login: str
    password: str
    country: str
    available_subs: int
    query_params: str
    server_ip: str


async def get_server_with_most_available_subs() -> Server:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT * FROM servers 
        WHERE available_subs > 0
        ORDER BY available_subs DESC 
        LIMIT 1
        """
    )
    await conn.close()
    return Server(**result) if result else None


async def increment_available_subs(server_id: int):
    conn = await get_connection()
    await conn.execute(
        """
        UPDATE servers SET available_subs = available_subs + 1 WHERE server_id = $1
        """,
        server_id,
    )
    await conn.close()


async def decrement_available_subs(server_id: int):
    conn = await get_connection()
    await conn.execute(
        """
        UPDATE servers SET available_subs = available_subs - 1 WHERE server_id = $1
        """,
        server_id,
    )
    await conn.close()


async def get_server_by_id(server_id: int) -> Server:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT * FROM servers WHERE server_id = $1
        """,
        server_id,
    )
    await conn.close()
    return Server(**result) if result else None


async def get_users_with_active_subs():
    conn = await get_connection()
    results = await conn.fetch(
        """
        SELECT u.telegram_id FROM users u
        JOIN subscriptions s ON u.user_id = s.user_id
        WHERE s.status = TRUE
        """
    )
    await conn.close()
    return [int(result['telegram_id']) for result in results]


async def get_sub_server_id_by_telegram_id(telegram_id: int) -> int:
    conn = await get_connection()
    result = await conn.fetchrow(
        """
        SELECT s.server_id FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE u.telegram_id = $1 AND s.status = TRUE
        """,
        telegram_id,
    )
    await conn.close()
    return result['server_id'] if result else None


asyncio.run(create_tables())
