import random
import string


def generate_email(tg_user_id: int, tg_username: str) -> str:
    random_letters = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f'@{tg_username}-{tg_user_id}-{random_letters}'
