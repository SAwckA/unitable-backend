from starlette.responses import Response

from core.app import app
from settings.config import JWTConfig

from . import schemas, views


@app.post('/login')
async def login(form: schemas.LoginForm, response: Response):
    """
    Аутентификация пользователя по паролю
    Устанавливает Access Token в куки, время жизни либо сессия, либо из конфига
    """
    token = await views.login_view(form)

    response.status_code = 200

    """
     TO DO:
        Сделать тело запроса с фулл инфой пользователя
     response.body =
    """

    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        expires=JWTConfig.access_token_exp.seconds if not form.remember else None,
    )

    return response


@app.post('/register')
async def register(form: schemas.RegisterForm):
    """
    Регистрация пользователя
    Успешна -> HTTP 200 'OK'
    Пользователь уже существует -> HTTP 409
    """
    await views.register_view(form)

    return 'OK'
