import datetime

from jose import jws, jwt
from shared.infrastructure import get_settings

settings = get_settings()


class SecuritySchema:
    def __init__(self):
        self.__secret_key = settings.SECRET_KEY
        self.__algorithm = settings.ALGORITHM
        self.__access_token_expire_minutes = 30

    def create_access_token(self, user: dict):
        access_token_expires = datetime.timedelta(
            minutes=self.__access_token_expire_minutes)
        expire = datetime.datetime.utcnow() + access_token_expires
        to_encode = {
            "sub": user,
            "exp": expire
        }
        return jwt.encode(to_encode, self.__secret_key, self.__algorithm)

    def decode_access_token(self, token: str) -> bytes:
        return jws.verify(token, self.__secret_key, self.__algorithm)
