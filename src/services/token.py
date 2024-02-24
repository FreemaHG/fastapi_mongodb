from fastapi import Response
from fastapi_jwt_auth import AuthJWT

from src.utils.token import SetTokenUtils


class TokenService:
    """
    Установка и обновление токена
    """

    @classmethod
    async def refresh(cls, response: Response, user_id: int, Authorize: AuthJWT) -> None:
        """
        Установка токенов в куки
        """
        await SetTokenUtils.access(response=response, user_id=user_id, Authorize=Authorize)
        await SetTokenUtils.logged(response=response)

    @classmethod
    async def set_cookies(cls, response: Response, user_id: int, Authorize: AuthJWT) -> None:
        """
        Установка токенов в куки
        """
        await cls.refresh(response=response, user_id=user_id, Authorize=Authorize)
        await SetTokenUtils.refresh(response=response, user_id=user_id, Authorize=Authorize)
