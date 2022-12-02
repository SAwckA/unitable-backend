from fastapi import Cookie

from auth.tokens import AccessPayload, JWTAccessToken


def validate(token):
    user = JWTAccessToken.validate_token(token)
    if isinstance(user, AccessPayload):
        return user
    raise user


class AccessTokenAuth:
    def __init__(
        self,
        access_token: str = Cookie('access_token'),
    ):
        self.user: AccessPayload = validate(access_token)
