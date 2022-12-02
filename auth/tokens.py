""" Алгоритмы работы jwt в auth сервисе"""

import base64
import datetime
import os
from abc import ABC, abstractmethod
from typing import Type

import jwt as json_web_token
from fastapi import HTTPException
from pydantic import BaseModel

import utils.hash_algs as hash_algs
from settings.config import JWTConfig

SECRET_KEY = JWTConfig.secret_key


class TokensPair(BaseModel):
    """
    Объект представления пары токенов
    (замена обращений со словарей на типипзированные классы)
    """

    access: str
    refresh: str


class BaseTokenPayload(BaseModel):
    """Базовая полезная нагрузка токена"""

    jti: str = ''
    sub: str
    iss: str


class AccessPayload(BaseTokenPayload):
    """Полезная нагрузка access токена"""

    # App service info
    id: int
    username: str

    # Custom services
    sid: str = ''

    # RFC Standard
    sub: str = 'access'
    iss: str = 'auth_service'


class RefreshPayload(BaseTokenPayload):
    """Полезная нагрузка refresh токена"""

    id: int = 0
    username: str = ''
    is_verified: bool = False
    sid: str = ''
    # RFC Standard
    iss: str = 'auth_service'
    sub: str = 'refresh'


payload_class_hint = AccessPayload | RefreshPayload | BaseTokenPayload

payload_class_exception_hint = AccessPayload | RefreshPayload | BaseTokenPayload | HTTPException


class AbstractJWT(ABC):
    """Интерфейс токена"""

    payload_class: Type[payload_class_hint] = BaseTokenPayload  # noqa
    token_type: str

    @abstractmethod
    def encode_token(
        self,
        data: payload_class_hint,
        sid: str = '',
    ) -> tuple[str, str]:
        """Возвращает токен и sid"""
        ...

    @abstractmethod
    def decode_token(self, token: str) -> payload_class_hint:
        """Возвращает полезную нагрузку токена"""
        ...

    @abstractmethod
    def validate_token(self, token: str) -> payload_class_exception_hint:
        """Проверяет полученный токен"""
        ...

    @abstractmethod
    def check_sub(self, token_payload: payload_class_hint) -> payload_class_exception_hint:
        """Проверяет назначение токена"""


class BaseJWT(AbstractJWT):
    """Базовая реализация jwt токена"""

    payload_class: Type[payload_class_hint] = BaseTokenPayload
    token_type: str

    @classmethod
    def get_exp_time(cls, token_type: str) -> int:
        """Установка времени истечения токена"""

        match token_type:
            case 'access':
                time_delta = JWTConfig.access_token_exp

            case 'refresh':
                time_delta = JWTConfig.refresh_token_exp

            case _:
                time_delta = JWTConfig.access_token_exp

        return int(datetime.datetime.now().timestamp()) + int(time_delta.total_seconds())

    @classmethod
    def create_sid(cls):
        """
        Уникальная строка сессии
        Создаётся 1 раз, при логине по паролю
        Наследуется новыми refresh токенами
        """
        return hash_algs.generate_token_sid()

    @classmethod
    def create_jti(cls):
        """Уникальная строка токена, используется как id"""
        return base64.b64encode(os.urandom(18)).decode('utf-8')

    @classmethod
    def encode_token(
        cls,
        data: payload_class_hint,
        sid: str = '',
        token_type: str = '',
    ) -> tuple[str, str]:
        """Шифровка токена"""
        payload = cls.payload_class(**(data.dict())).dict()
        payload['jti'] = base64.b64encode(os.urandom(18)).decode('utf-8')
        payload['exp'] = cls.get_exp_time(cls.token_type)

        if sid is None:
            sid = cls.create_sid()

        payload['sid'] = sid

        token = json_web_token.encode(
            payload=payload,
            key=SECRET_KEY,
            algorithm=JWTConfig.jwt_alg,
        )
        return token, sid

    @classmethod
    def decode_token(cls, token: str) -> payload_class_hint:
        """Расшифровка токена"""
        # header = json_web_token.get_unverified_header(token)

        payload: dict = json_web_token.decode(
            token,
            key=SECRET_KEY,
            algorithms=[
                JWTConfig.jwt_alg,
            ],
        )

        return cls.payload_class(**payload)

    @classmethod
    def validate_token(cls, token: str) -> payload_class_exception_hint:
        """Валидация токена для расшифровки"""
        try:
            payload = cls.decode_token(token)

        except (
            json_web_token.ExpiredSignatureError,
            json_web_token.DecodeError,
        ) as e:

            if isinstance(
                e,
                json_web_token.ExpiredSignatureError,
            ):
                return HTTPException(
                    status_code=401,
                    detail='Token is expired',
                )

            if isinstance(e, json_web_token.DecodeError):
                return HTTPException(
                    status_code=401,
                    detail='Invalid token',
                )

            return HTTPException(
                status_code=401,
                detail=f'Access token error: {e}',
            )

        return payload

    @classmethod
    def check_sub(cls, token_payload: payload_class_hint) -> payload_class_exception_hint:
        """Проверка назначения"""
        if token_payload.sub == cls.token_type:
            return token_payload
        return HTTPException(
            status_code=401,
            detail='Invalid token sub',
        )


class JWTRefreshToken(BaseJWT):
    """Реализация refresh токена"""

    payload_class: Type[payload_class_hint] = RefreshPayload
    token_type = 'refresh'

    @classmethod
    def encode_token(
        cls,
        data: payload_class_hint,
        sid: str = '',
        token_type: str = token_type,
    ) -> tuple[str, str]:
        """Переопределение класса полезной нагрузки"""
        return super().encode_token(data, sid, token_type)


class JWTAccessToken(BaseJWT):
    """Реализация access токена"""

    payload_class: Type[payload_class_hint] = AccessPayload
    token_type = 'access'

    @classmethod
    def encode_token(
        cls,
        data: payload_class_hint,
        sid: str = '',
        token_type: str = token_type,
    ) -> tuple[str, str]:
        """Переопределение класса полезной нагрузки"""
        return super().encode_token(data, sid, token_type)
