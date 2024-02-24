from datetime import timedelta

from fastapi import Response
from fastapi_jwt_auth import AuthJWT

from src.config import settings


class SetTokenUtils:
    """
    Установка токена
    """

    __ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
    __REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
    __access_token = 'access_token'
    __refresh_token = 'refresh_token'
    __logged_in = 'logged_in'

    @classmethod
    async def __create_access(cls, user_id: int, Authorize: AuthJWT):
        """
        Создаем токен доступа (записываем id пользователя в токен)
        """
        access_token = Authorize.create_access_token(
            subject=str(user_id), expires_time=timedelta(minutes=cls.__ACCESS_TOKEN_EXPIRES_IN))

        return access_token

    @classmethod
    async def __create_refresh(cls, user_id: int, Authorize: AuthJWT):
        """
        Создаем токен обновления (записываем id пользователя в токен)
        :param user_id:
        :param Authorize:
        :return:
        """
        refresh_token = Authorize.create_refresh_token(
            subject=str(user_id), expires_time=timedelta(minutes=cls.__REFRESH_TOKEN_EXPIRES_IN))

        return refresh_token

    @classmethod
    async def access(cls, response: Response, user_id: int, Authorize: AuthJWT):
        """
        Сохранение токена доступа в куки объекта запроса
        """
        access_token = await cls.__create_access(user_id=user_id, Authorize=Authorize)

        response.set_cookie(
            cls.__access_token,
            access_token,
            cls.__ACCESS_TOKEN_EXPIRES_IN * 60,
            cls.__ACCESS_TOKEN_EXPIRES_IN * 60,
            '/',
            None,
            False,
            True,
            'lax'
        )

    @classmethod
    async def refresh(cls, response: Response, user_id: int, Authorize: AuthJWT) -> None:
        """
        Сохранение токена в куки объекта запроса
        """

        refresh_token = await cls.__create_refresh(user_id=user_id, Authorize=Authorize)

        response.set_cookie(
            cls.__refresh_token,
            refresh_token,
            cls.__REFRESH_TOKEN_EXPIRES_IN * 60,
            cls.__REFRESH_TOKEN_EXPIRES_IN * 60,
            '/',
            None,
            False,
            True,
            'lax'
        )

    @classmethod
    async def logged(cls, response: Response) -> None:
        """
        Сохранение токена в куки объекта запроса
        """

        response.set_cookie(
            cls.__logged_in,
            'True',
            cls.__ACCESS_TOKEN_EXPIRES_IN * 60,
            cls.__ACCESS_TOKEN_EXPIRES_IN * 60,
            '/',
            None,
            False,
            False,
            'lax'
        )
