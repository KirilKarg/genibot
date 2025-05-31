from database.db import get_user


async def is_god(event):
    user = await get_user(event.sender_id)
    return user and user[3] in ('god')

async def is_admin(event):
    user = await get_user(event.sender_id)
    return user and user[3] in ('admin', 'god')

async def is_vip(event):
    user = await get_user(event.sender_id)
    return user and user[3] in ('vip','admin', 'god')

async def check_role(event, required_role):
    user = await get_user(event.sender_id)
    return user and user[3] == required_role
