from fastapi import HTTPException

from utils.hash_algs import check_password, create_password

from . import db_operations, schemas
from .tokens import AccessPayload, JWTAccessToken


async def login_view(
    credentials: schemas.LoginForm,
) -> str:
    """
    Аутентификация пользователя по паролю
    Возвращает Access токен
    Несовпадения данных в бд -> HTTP 404
    """

    user = await db_operations.get_user_by_username(credentials.username)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail='Invalid credentials',
        )

    if not check_password(credentials.password, user.password):
        raise HTTPException(
            status_code=404,
            detail='Invalid credentials',
        )

    token, _ = JWTAccessToken.encode_token(AccessPayload(username=user.username, id=user.id))

    return token


async def register_view(
    data: schemas.RegisterForm,
) -> None:
    """
    Регистрация нового пользователя
    Если пользователь есть в базе данных -> HTTP 409
    """
    res = await db_operations.insert_new_user(
        username=data.username,
        password=create_password(data.password),
        email=data.email,
        fio=data.fio,
    )

    if not res:
        raise HTTPException(
            status_code=409,
            detail='User already exist',
        )
