import re
from datetime import datetime

from pydantic import BaseModel, validator


class UserLogin(BaseModel):
    """Объект пользователя из базы данных для логина"""

    id: int
    username: str
    email: str
    password: str


class UserDetail(BaseModel):
    """Полный объект пользователя"""

    username: str
    email: str
    fio: str
    created_at: datetime
    tg: str
    vk: str
    phone: str


class RegisterForm(BaseModel):
    """Форма регистрации пользователя"""

    username: str
    password: str
    email: str
    fio: str

    @classmethod
    @validator('username')
    def validate_username(cls, v):
        if ' ' in v:
            raise ValueError('Username can not contain spaces')

        if len(v) < 4:
            raise ValueError('Username length must be > 3')

        if len(v) > 29:
            raise ValueError('Username length must be < 30')

        return v

    @classmethod
    @validator('password')
    def validate_password(cls, v):
        has_special = False
        for s in v:
            if s in " #$%&'()*+,-./:;<=>?@[\\]^_`{|}~":
                has_special = True
                continue

        if not has_special:
            raise ValueError('Password must content special symbol')

        if len(v) < 8:
            raise ValueError('Password length must be >= 8')

        return v

    @classmethod
    @validator('email')
    def validate_email(cls, v):
        r = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        regex = re.compile(r)
        if not re.fullmatch(regex, v):
            raise ValueError('Invalid email')

        return v


class LoginForm(BaseModel):
    """Форма аутентификации по паролю пользователя"""

    username: str
    password: str
    remember: bool = True
