from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from loguru import logger

from src.repositories.user import UserRepository
from src.serializers.user import user_entity
from src.utils.exeptions import UserNotFound, NotVerified


async def require_user(Authorize: AuthJWT = Depends()) -> int:
    """
    Проверка токена (аутентификации) пользователя
    """

    try:
        Authorize.jwt_required()  # Включаем файл cookie токена доступа в запрос
        user_id = Authorize.get_jwt_subject()  # Извлекаем данные пользователя (id пользователя) из cookie

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

    user_db = await UserRepository.get_for_id(user_id=user_id)
    user = await user_entity(user_db)

    if not user:
        raise UserNotFound('Пользователь больше не существует')

    if not user["verified"]:
        raise NotVerified('У вас не подтвержденная запись')

    return user_id
