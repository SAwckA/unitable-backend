import asyncpg  # type: ignore # noqa
from fastapi import FastAPI

from core.database import DB

app = FastAPI()
db = DB()


@app.on_event('startup')
async def startup():
    await db.create_pool()


@app.on_event('shutdown')
async def shutdown():
    await db.close_pool()


@app.get('/')
async def health():
    conn: asyncpg.Connection
    async with db.pool.acquire() as conn:
        a: list[asyncpg.Record]
        a = await conn.fetch("""select id, username from public.user;""")
        for x in a:
            print(x)
        await conn.close()

    return dict(a[0])


import auth.routes  # type: ignore # noqa
