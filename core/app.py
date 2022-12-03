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
async def health() -> str:
    """ Health check """
    return "OK"


import auth.routes  # type: ignore # noqa
import users.routes # type: ignore # noqa
import journal.routes # type: ignore # noqa
