import os
from datetime import timedelta

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def env_get(arg):
    """Упрощение"""
    return os.environ.get(arg)


class JWTConfigClass(BaseModel):
    """Настройка JWT"""

    jwt_alg: str = 'HS512' if env_get('JWT_ALG') is None else env_get('JWT_ALG')

    access_token_exp: timedelta = (
        timedelta(days=30)
        if env_get('JWT_ACCESS_EXPIRE') is None
        else timedelta(days=int(env_get('JWT_ACCESS_EXPIRE')))
    )

    refresh_token_exp: timedelta = (
        timedelta(days=60)
        if env_get('JWT_REFRESH_EXPIRE') is None
        else timedelta(days=int(env_get('JWT_REFRESH_EXPIRE')))
    )

    secret_key: str = env_get('SECRET_KEY')


class DatabaseConfigClass(BaseModel):
    """Параметры подключения к базе данных"""

    DB_NAME: str = env_get('DB_NAME')
    DB_USER: str = env_get('DB_USER')
    DB_PASS: str = env_get('DB_PASS')

    DB_HOST: str = 'localhost' if env_get('DB_HOST') is None else env_get('DB_HOST')

    DB_PORT: int = 5432 if env_get('DB_PORT') is None else env_get('DB_PORT')


JWTConfig: JWTConfigClass = JWTConfigClass()
DatabaseConfig: DatabaseConfigClass = DatabaseConfigClass()
