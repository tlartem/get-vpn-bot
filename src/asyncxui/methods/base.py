import aiohttp

import asyncxui
from asyncxui import errors


class Base:
    async def request(
        self: 'asyncxui.XUI', path: str, method: str, params: dict = None
    ) -> aiohttp.ClientResponse:
        """Request to the xui panel.

        Parameters:
            path (``str``):
                The request path, you can see all of them in https://github.com/alireza0/x-ui#api-routes

            method (``str``):
                The request method, GET or POST

            params (``dict``, optional):
                The request parameters, None is set for default but it's necessary for some POST methods

        Returns:
            `~aiohttp.ClientResponse`: On success, the response is returned.
        """

        if path == 'login':
            url = f'{self.full_address}/login'
        else:
            url = f'{self.full_address}/{self.api_path}/inbounds/{path}'

        if self.session_string:
            cookie = {self.cookie_name: self.session_string}
        else:
            cookie = None

        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, cookies=cookie, ssl=False) as response:
                    return response
            elif method == 'POST':
                async with session.post(
                    url, cookies=cookie, data=params, ssl=False
                ) as response:
                    return response

    async def verify_response(
        self: 'asyncxui.XUI', response: aiohttp.ClientResponse
    ) -> aiohttp.ClientResponse:
        if response.status != 404 and response.headers.get('Content-Type').startswith(
            'application/json'
        ):
            return response

        raise errors.NotFound()
