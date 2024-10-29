def config_generator(config=dict, query_params: str = None) -> str:
    string = 'vless://{}@{}:443?{}{}'.format(
        config['uuid'],
        config['server_ip'],
        query_params,
        config['email'],
    )

    return string


# vless://67e73c62-7557-4316-b811-d2e7230c4c25@194.87.219.215:443/?#main-%40qwertyums
