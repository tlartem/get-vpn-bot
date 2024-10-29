from typing import Any

import asyncxui
from asyncxui import errors


class Login:
    async def login(self: 'asyncxui.XUI', username: str, password: str) -> Any:
        """Login into xui panel.

        Parameters:
            username (``str``):
                Username of panel

            password (``str``):
                Password of panel

        Returns:
            `~Any`: On success, True is returned else an error will be raised
        """

        if self.session_string:
            raise errors.AlreadyLogin()

        send_request = await self.request(
            path='login',
            method='POST',
            params={'username': username, 'password': password},
        )

        if send_request.status == 200:
            self.session_string = send_request.cookies.get(self.cookie_name)

            if self.session_string:
                return True

        raise errors.BadLogin()
