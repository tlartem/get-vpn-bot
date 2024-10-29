from typing import Union

import asyncxui
from asyncxui import errors


class Inbounds:
    async def get_inbounds(self: 'asyncxui.XUI') -> Union[dict, errors.NotFound]:
        """Get inbounds of the xui panel."""

        if self.panel == 'alireza':
            path = ''
        elif self.panel == 'sanaei':
            path = 'list'

        response = await self.request(path=path, method='GET')

        return await self.verify_response(response)

    async def get_inbound(
        self: 'asyncxui.XUI', inbound_id: int
    ) -> Union[dict, errors.NotFound]:
        """Get inbounds of the xui panel."""

        response = await self.request(path=f'get/{inbound_id}', method='GET')

        return self.verify_response(response)
