from base64 import b64encode
from hashlib import sha256
from os import urandom
from zlib import adler32


def _sha256_password(salted_password: str) -> str:
    """Хэширует солёный пароль"""
    hashed_password = sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password


def _generate_salt() -> str:
    """Генерирует соль длиной 16 символов"""

    return b64encode(urandom(12)).decode('utf-8')


def generate_token(size: int = 64) -> str:
    """Генерирует случайную строку указаной длины, (стандартная 64)"""

    return sha256(b64encode(urandom(size))).hexdigest()


def create_password(password: str) -> str:
    """Смешивает соль и хэшированный пароль"""

    salt = _generate_salt()
    hashed_password = _sha256_password(salt + password)

    password = f'{salt}${hashed_password}'
    return password


def check_password(original_pwd: str, pwd: str) -> bool:
    """Сравнивает полученный пароль с уже хэшированным"""
    salt, pwd = pwd.split('$')

    if _sha256_password(salt + original_pwd) == pwd:
        return True
    return False


def generate_token_sid() -> str:
    """Создаёт sid jwt токена"""
    return generate_token()


def hash_sum(*args) -> int:
    """Подсчитывает хэш-сумму из всех аргументов
    (происходит слияние без пробелов) -> int32"""
    return adler32(''.join(str(x) for x in args).encode('utf-8'))
