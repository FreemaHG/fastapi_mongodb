from fastapi import Response, status, Depends, HTTPException

from src.repositories.user import UserRepository
from src.routes.base import APIBaseRouter
from src.serializers.user import user_entity
from src.schemas.user import CreateUserSchema, UserResponseSchema, LoginUserSchema
from src.services.token import TokenService
from src.services.user import UserService
from src.utils.check_authorization import require_user
from src.utils.password import verify_password
from src.oauth2 import AuthJWT
from src.config import settings


_ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
_REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

router = APIBaseRouter(tags=['Auth'])

@router.post(
    '/auth/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
)
async def create_user(user_data: CreateUserSchema):
    """
    Регистрация пользователя
    """

    user = await UserRepository.get_for_email(email=user_data.email.lower())

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким email уже зарегистрирован'
        )

    # Проверка введенных паролей
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароли не совпадают'
        )

    new_user = await UserService.create(user_data=user_data)

    return {'status': 'success', 'user': new_user}


@router.post('/auth/login')
async def login(
        user_data: LoginUserSchema,
        response: Response,
        Authorize: AuthJWT = Depends(),
):
    """
    Авторизация пользователя
    """

    db_user = await UserRepository.get_for_email(email=user_data.email.lower())

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь с таким email не зарегистрирован'
        )

    user = await user_entity(db_user)  # Сериализуем данные пользователя в словарь

    # Проверяем введенный пароль с хэшированным из БД
    # if not verify_password(user_data.password, user['password']):
    if not await verify_password(user_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароль не верен'
        )

    await TokenService.set_cookies(response=response, user_id=user['id'], Authorize=Authorize)

    return {'status': 'success'}


@router.get('/auth/refresh')
async def refresh_token(
        response: Response,
        Authorize: AuthJWT = Depends())\
        :
    """
    Обновление токена доступа пользователя
    """

    user_id = None

    try:
        # Гарантирует, что файл cookie с токеном обновления был включен во входящий запрос
        Authorize.jwt_refresh_token_required()
        user_id = Authorize.get_jwt_subject()  # Извлекаем данные из токена (id пользователя)

    except Exception as e:
        error = e.__class__.__name__

        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пожалуйста, предоставьте токен обновления'
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось обновить токен доступа'
        )

    user = await UserService.get(user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь, принадлежащий к этому токену, больше не существует'
        )

    await TokenService.refresh(response=response, user_id=user['id'], Authorize=Authorize)

    return {'message': 'OK'}


@router.get(
    '/auth/logout',
    status_code=status.HTTP_200_OK
)
async def logout(
        response: Response,
        Authorize: AuthJWT = Depends(),
        user_id: str = Depends(require_user)):
    """
    Выход пользователя из учетной записи
    """

    Authorize.unset_jwt_cookies()  # Удаление файлов cookie из браузера (клиента)
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
