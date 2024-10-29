import asyncio

from asyncxui import XUI


async def main():
    panel = XUI(full_address='https://goodypoody.space/kuper', panel='sanaei')
    try:
        print(await panel.login('kilpir', 'piska98goto'))
        print(await panel.delete_client(1, uuid='5d23ec2b-8739-429b-848f-ecb4a3ee7a9d'))
    except Exception as e:
        print(f'Произошла ошибка: {e}')


if __name__ == '__main__':
    asyncio.run(main())
