import os

from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администратора
ADMIN_TG_ID = int(os.getenv('ADMIN_TG_ID'))
ADMIN_TG_USERNAME = os.getenv('ADMIN_TG_USERNAME')

# Данные для подключения к базе данных
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')

DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

# Ссылка на инструкцию
INSTRUCTION_LINK = os.getenv('INSTRUCTION_LINK')

# ID чата подписки
CHAT_TG_ID = os.getenv('CHAT_TG_ID')

IS_DEBUG = False


# Весовые коэффициенты
VPN_USAGE_WEIGHTS = {
    'Очень редко': 0.5,
    'Иногда': 0.75,
    'Средне': 1.0,
    'Постоянно': 2.0,
}

YOUTUBE_USAGE_WEIGHT = {
    'Да': 1.0,
    'Нет': 0.0,
}
