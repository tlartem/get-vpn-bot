import random
import string


def generate_email(tg_user_id: int) -> str:
    random_letters = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f'{tg_user_id}-{random_letters}'
