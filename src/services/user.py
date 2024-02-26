from datetime import datetime
from typing import Dict

from loguru import logger

from src.repositories.user import UserRepository
from src.schemas.user import CreateUserSchema
from src.serializers.user import user_response_entity
from src.utils.password import hash_password


class UserService:

    @classmethod
    async def get(cls, user_id: str) -> Dict | None:
        """
        Возврат пользователя по id
        :param user_id: id пользователя
        :return: словарь с данными пользователя либо None
        """

        # Поиск пользователя в БД
        user = await UserRepository.get_for_id(user_id=user_id)

        # Сериализация данных
        user_data = await user_response_entity(user)

        return user_data

    @classmethod
    async def create(cls, user_data: CreateUserSchema) -> Dict:
        """
        Сохранение пользователя в БД
        :param user_data: данные нового пользователя
        :return: словарь с данными нового пользователя из БД
        """

        user_data.role = 'user'
        user_data.verified = True
        user_data.email = user_data.email.lower()
        user_data.created_at = datetime.utcnow()
        user_data.updated_at = user_data.created_at
        user_data.password = await hash_password(user_data.password)  # Сохраняем хэш пароля в БД

        del user_data.password_confirm  # Удаляем из словаря с входными данными пароль-подтверждение

        # Добавляем пользователя в БД (вернется id пользователя)
        user_id = await UserRepository.create(user_data=user_data)

        # Получаем только что созданного пользователя из БД по id
        new_user_db = await UserRepository.get_for_id(user_id=user_id)

        # Передав в сериализатор user_response_entity данные пользователя,
        # мы тем самым удаляем из ответа чувствительные данные (пароль)
        new_user = await user_response_entity(new_user_db)
        logger.info(f'Пользователь успешно зарегистрирован')

        return new_user
