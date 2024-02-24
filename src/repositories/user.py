from bson.objectid import ObjectId

from src.database import User
from src.schemas.user import CreateUserSchema


class UserRepository:
    """
    CRUD операции с пользователем
    """

    @classmethod
    async def create(cls, user_data: CreateUserSchema) -> int:
        """
        Создание пользователя
        :param user_data: данные нового пользователя
        :return: id нового пользователя
        """
        result = await User.insert_one(user_data.dict())

        return result.inserted_id

    @classmethod
    async def get_for_id(cls, user_id: int) -> User:
        """
        Поиск пользователя в БД по id
        :param user_id: id пользователя для поиска
        :return: объект пользователя
        """
        user = await User.find_one({'_id': ObjectId(str(user_id))})

        return user

    @classmethod
    async def get_for_email(cls, email: str) -> User:
        """
        Поиск пользователя в БД по email
        :param email: email для поиска
        :return: объект пользователя
        """
        user = await User.find_one({'email': email})

        return user
