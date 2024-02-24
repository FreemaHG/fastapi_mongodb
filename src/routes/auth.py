from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException
from loguru import logger

from src import oauth2
from src.database import User
from src.serializers.user import user_entity, user_response_entity
from src.schemas.user import UserBaseSchema, CreateUserSchema, UserOutSchema, UserResponseSchema, LoginUserSchema
from src.utils.password import hash_password, verify_password
from src.oauth2 import AuthJWT
from src.config import settings


_ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
_REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

router = APIRouter(tags=['auth'])

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
)
async def create_user(user_data: CreateUserSchema):
    """
    Регистрация пользователя
    """

    # Ищем пользователя в БД по email
    user = User.find_one({'email': user_data.email.lower()})

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

    # Хэширование и пересохранение пароля
    user_data.password = hash_password(user_data.password)
    del user_data.password_confirm  # Удаляем из словаря с входными данными пароль-подтверждение

    # Сохранение нового пользователя
    user_data.role = 'user'
    user_data.verified = True
    user_data.email = user_data.email.lower()
    user_data.created_at = datetime.utcnow()
    user_data.updated_at = user_data.created_at

    # Добавляем пользователя в БД (вернется id пользователя)
    result = User.insert_one(user_data.dict())

    # Получаем только что созданного пользователя из БД по id
    # Передав в сериализатор user_response_entity данные пользователя,
    # мы тем самым удаляем из ответа чувствительные данные (пароль)
    new_user = user_response_entity(User.find_one({'_id': result.inserted_id}))

    return {'status': 'success', 'user': new_user}


@router.post('/login')
async def login(
        user_data: LoginUserSchema,
        response: Response,
        Authorize: AuthJWT = Depends(),
):
    """
    Авторизация пользователя
    """

    # Поиск пользователя в БД по email
    db_user = User.find_one({'email': user_data.email.lower()})

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь с таким email не зарегистрирован'
        )

    user = user_entity(db_user)  # Сериализуем данные пользователя в словарь

    # Проверяем введенный пароль с хэшированным из БД
    if not verify_password(user_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароль не верен'
        )

    # Создаем токен доступа (записываем id пользователя в токен)
    access_token = Authorize.create_access_token(
        subject=str(user["id"]), expires_time=timedelta(minutes=_ACCESS_TOKEN_EXPIRES_IN))

    # Создаем токен обновления (записываем id пользователя в токен)
    refresh_token = Authorize.create_refresh_token(
        subject=str(user["id"]), expires_time=timedelta(minutes=_REFRESH_TOKEN_EXPIRES_IN))

    # Сохраняем токены обновления и доступа в файлах cookie
    response.set_cookie('access_token', access_token, _ACCESS_TOKEN_EXPIRES_IN * 60,
                        _ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.set_cookie('refresh_token', refresh_token,
                        _REFRESH_TOKEN_EXPIRES_IN * 60, _REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.set_cookie('logged_in', 'True', _ACCESS_TOKEN_EXPIRES_IN * 60,
                        _ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    return {'status': 'success', 'access_token': access_token}


@router.get('/refresh')
def refresh_token(
        response: Response,
        Authorize: AuthJWT = Depends())\
        :
    """
    Обновление токена доступа пользователя
    """

    try:
        # Гарантирует, что файл cookie с токеном обновления был включен во входящий запрос
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()  # Извлекаем данные из токена (id пользователя)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Не удалось обновить токен доступа'
            )

        # Поиск пользователя в БД по id из токена
        user = user_entity(User.find_one({'_id': ObjectId(str(user_id))}))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь, принадлежащий к этому токену, больше не существует'
            )

        access_token = Authorize.create_access_token(
            subject=str(user["id"]), expires_time=timedelta(minutes=_ACCESS_TOKEN_EXPIRES_IN))

    except Exception as e:
        error = e.__class__.__name__

        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пожалуйста, предоставьте токен обновления'
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    # Сохраняем токены обновления и доступа в файлах cookie
    response.set_cookie('access_token', access_token, _ACCESS_TOKEN_EXPIRES_IN * 60,
                        _ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.set_cookie('logged_in', 'True', _ACCESS_TOKEN_EXPIRES_IN * 60,
                        _ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    return {'access_token': access_token}


@router.get(
    '/logout',
    status_code=status.HTTP_200_OK
)
def logout(
        response: Response,
        Authorize: AuthJWT = Depends(),
        user_id: str = Depends(oauth2.require_user)):
    """
    Выход пользователя из учетной записи
    """

    Authorize.unset_jwt_cookies()  # Удаление файлов cookie из браузера (клиента)
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
