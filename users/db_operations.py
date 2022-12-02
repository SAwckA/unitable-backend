import asyncpg

from . import schemas
from core.app import db


async def get_user_by_id(user_id: int) -> schemas.UserDetail | None:
    conn: asyncpg.Pool
    async with db.pool.acquire() as conn:
        user = await conn.fetch("""select
            username,
            email,
            fio,
            tg,
            vk,
            phone
            from public.user where id=$1
        """, user_id)

    if user:
        return schemas.UserDetail(**dict(user[0]))

    return None
