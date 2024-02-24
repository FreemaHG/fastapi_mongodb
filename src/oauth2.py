import base64
from typing import List
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from src.config import settings


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
