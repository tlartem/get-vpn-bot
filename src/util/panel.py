from lib.asyncxui import XUI
from src.db.entity import Server


class Panel:
    @staticmethod
    async def init(server: Server) -> XUI:
        panel = XUI(full_address=server.host, panel='sanaei')
        await panel.login(server.login, server.password)
        return panel

    @staticmethod
    async def check_login(host: str, login: str, password: str) -> bool:
        panel = XUI(full_address=host, panel='sanaei')
        result: bool = False
        try:
            result = await panel.login(login, password)
        except Exception:
            pass

        return result
