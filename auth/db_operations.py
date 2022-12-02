import asyncpg  # type: ignore # noqa

from core.app import db

from . import schemas


async def get_user_by_username(
    username: str,
) -> None | schemas.UserLogin:
    """Выборка пользователя по username, где username = {username, email}"""
    conn: asyncpg.Connection
    sql = """\
        select
            id,
            username,
            email,
            password
        from public.user where
            username=$1 or email=$2"""
    async with db.pool.acquire() as conn:
        user: list[asyncpg.Record]
        user = await conn.fetch(sql, username, username)

    if not user:
        return None

    return schemas.UserLogin(**dict(user[0]))


async def insert_new_user(
    username: str,
    password: str,
    email: str,
    fio: str,
) -> bool:
    """
    Записывает нового пользователя в базу данных
    Возвращает был ли создан или нет
    """
    conn: asyncpg.Connection
    sql = """insert into public.user(
                                    username,
                                    password,
                                    email,
                                    fio,
                                    created_at
                                    ) values ($1, $2, $3, $4, NOW()::date)"""

    async with db.pool.acquire() as conn:
        try:
            await conn.execute(
                sql,
                username,
                password,
                email,
                fio,
            )

        except asyncpg.UniqueViolationError:
            return False

    return True
