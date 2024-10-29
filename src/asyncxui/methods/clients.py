import json
from typing import Union

import asyncxui
from asyncxui import errors


class Clients:
    async def get_client(
        self: 'asyncxui.XUI', inbound_id: int, email: str = False, uuid: str = False
    ) -> Union[dict, errors.NotFound]:
        """Get client from the existing inbound."""

        get_inbounds = await self.get_inbounds()

        if not email and not uuid:
            raise ValueError()

        for inbound in get_inbounds['obj']:
            if inbound['id'] != inbound_id:
                continue

            settings = json.loads(inbound['settings'])

            for client in settings['clients']:
                if client['email'] != email and client['id'] != uuid:
                    continue

                return client

        raise errors.NotFound()

    async def get_client_stats(
        self: 'asyncxui.XUI',
        inbound_id: int,
        email: str,
    ) -> Union[dict, errors.NotFound]:
        """Get client stats from the existing inbound."""

        get_inbounds = await self.get_inbounds()

        if not email:
            raise ValueError()

        for inbound in get_inbounds['obj']:
            if inbound['id'] != inbound_id:
                continue

            client_stats = inbound['clientStats']

            for client in client_stats:
                if client['email'] != email:
                    continue

                return client

        raise errors.NotFound()

    async def add_client(
        self: 'asyncxui.XUI',
        inbound_id: int,
        email: str,
        uuid: str,
        enable: bool = True,
        flow: str = '',
        limit_ip: int = 0,
        total_gb: int = 0,
        expire_time: int = 0,
        telegram_id: str = '',
        subscription_id: str = '',
    ) -> Union[dict, errors.NotFound]:
        """Add client to the existing inbound."""

        settings = {
            'clients': [
                {
                    'id': uuid,
                    'email': email,
                    'enable': enable,
                    'flow': flow,
                    'limitIp': limit_ip,
                    'totalGB': total_gb,
                    'expiryTime': expire_time,
                    'tgId': telegram_id,
                    'subId': subscription_id,
                }
            ],
            'decryption': 'none',
            'fallbacks': [],
        }

        params = {'id': inbound_id, 'settings': json.dumps(settings)}

        response = await self.request(path='addClient', method='POST', params=params)

        return await self.verify_response(response)

    async def delete_client(
        self: 'asyncxui.XUI', inbound_id: int, email: str = False, uuid: str = False
    ) -> Union[dict, errors.NotFound]:
        """Delete client from the existing inbound."""

        find_client = await self.get_client(
            inbound_id=inbound_id, email=email, uuid=uuid
        )

        response = await self.request(
            path=f"{inbound_id}/delClient/{find_client['id']}", method='POST'
        )

        return await self.verify_response(response)

    async def update_client(
        self: 'asyncxui.XUI',
        inbound_id: int,
        email: str,
        uuid: str,
        enable: bool,
        flow: str,
        limit_ip: int,
        total_gb: int,
        expire_time: int,
        telegram_id: str,
        subscription_id: str,
    ) -> Union[dict, errors.NotFound]:
        """Add client to the existing inbound."""

        find_client = await self.get_client(
            inbound_id=inbound_id, email=email, uuid=uuid
        )

        settings = {
            'clients': [
                {
                    'id': uuid,
                    'email': email,
                    'enable': enable,
                    'flow': flow,
                    'limitIp': limit_ip,
                    'totalGB': total_gb,
                    'expiryTime': expire_time,
                    'tgId': telegram_id,
                    'subId': subscription_id,
                }
            ],
            'decryption': 'none',
            'fallbacks': [],
        }

        params = {'id': inbound_id, 'settings': json.dumps(settings)}

        response = await self.request(
            path=f"updateClient/{find_client['id']}", method='POST', params=params
        )

        return await self.verify_response(response)

    async def reset_client_traffic(
        self: 'asyncxui.XUI', inbound_id: int, email: str = False, uuid: str = False
    ) -> Union[dict, errors.NotFound]:
        """Delete client from the existing inbound."""

        find_client = await self.get_client(
            inbound_id=inbound_id, email=email, uuid=uuid
        )

        response = await self.request(
            path=f"{inbound_id}/resetClientTraffic/{find_client['email']}",
            method='POST',
        )

        return await self.verify_response(response)
