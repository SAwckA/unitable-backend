from pydantic import BaseModel, validator


class UserDetail(BaseModel):

    username: str
    email: str
    fio: str
    tg: str | None
    vk: str | None
    phone: str | None
