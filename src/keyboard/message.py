import src.config as config

NoAvailableServers = 'В данный момент нет доступных серверов'


def generate_link_message(link: str) -> str:
    return (
        f'<code>{link}</code>\n\n'
        f'<b>(Нажатие на ссылку скопирует её)</b>\n'
        f'Как поставить?: <a href="{config.INSTRUCTION_LINK}">ссылка</a>'
    )
