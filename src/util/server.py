from db.entity import Server


async def get_best_load_server(current_user_load_weight: float) -> Server:
    