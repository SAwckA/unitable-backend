from typing import Type

import asyncpg  # type: ignore

from settings.config import DatabaseConfig as DBcfg


class DB:
    def __init__(self):
        self.pool: asyncpg.Pool = Type[asyncpg.Pool]

    async def create_pool(self):
        """Создаёт новый пулл соединения"""

        psql_url = f'postgresql://{DBcfg.DB_USER}:{DBcfg.DB_PASS}@'
        psql_url += f'{DBcfg.DB_HOST}:{DBcfg.DB_PORT}/{DBcfg.DB_NAME}'
        self.pool: asyncpg.Pool = await asyncpg.create_pool(dsn=psql_url)

    async def close_pool(self):
        """Закрывает пулл соединений"""
        await self.pool.close()
