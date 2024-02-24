import base64
from typing import List

from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from loguru import logger
from pydantic import BaseModel

from src.config import settings
from src.database import User
from src.serializers.user import user_entity


class Settings(BaseModel):
    """
    Схема для настройки fastapi_jwt_auth пакета на использование открытого и закрытого ключей,
    алгоритма RS256 и для установки местоположения токена в файлы cookie
    """
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(
        settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        settings.JWT_PRIVATE_KEY).decode('utf-8')

# В приведенных выше фрагментах кода мы расшифровали открытый и закрытый ключи обратно в строки “UTF-8”,
# прежде чем присвоить их константам.

@AuthJWT.load_config
def get_config():
    return Settings()

class NotVerified(Exception):
    pass

class UserNotFound(Exception):
    pass

def require_user(Authorize: AuthJWT = Depends()) -> int:
    """
    Проверка токена (аутентификации) пользователя
    """

    try:
        Authorize.jwt_required()  # Включаем файл cookie токена доступа в запрос
        user_id = Authorize.get_jwt_subject()  # Извлекаем данные пользователя (id пользователя) из cookie
        user = user_entity(User.find_one({'_id': ObjectId(str(user_id))}))  # Поиск пользователя в БД

        if not user:
            raise UserNotFound('Пользователь больше не существует')

        if not user["verified"]:
            raise NotVerified('У вас не подтвержденная запись')

    except Exception as e:
        error = e.__class__.__name__
        logger.error(error)

        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не вошли в систему')

        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь больше не существует')

        if error == 'NotVerified':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Пожалуйста, подтвердите свою учетную запись')

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен недействителен или срок его действия истек')

    return user_id
