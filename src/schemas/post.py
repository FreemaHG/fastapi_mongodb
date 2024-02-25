from datetime import datetime
from typing import List

from pydantic import BaseModel, create_model
from bson import ObjectId

from src.schemas.base import BaseOutSchema
from src.schemas.mixin import DatetimeFormatterMixin
from src.schemas.user import UserOutSchema


class PostBaseSchema(BaseModel):
    """
    Базовая схема для записей
    """
    title: str
    content: str
    category: str
    image: str | None = None

    @classmethod
    def all_optional(cls, name: str):
        """
        Создает новую модель с теми же полями, но все необязательные.
        Использование: SomeOptionalModel = SomeModel.all_optional('SomeOptionalModel')
        """

        return create_model(
            name,
            __base__=cls,
            **{name: (info.annotation, None) for name, info in cls.__fields__.items()}
        )

    class Config:
        orm_mode = True  # Преобразование данных из БД в объект схемы без доп.валидации
        allow_population_by_field_name = True  # Инициализация модели, используя имена полей, а не только псевдонимов
        arbitrary_types_allowed = True  # Разрешаем использовать произвольные типы данных без доп.валидации
        json_encoders = {ObjectId: str}  # Автоматически преобразуем id в строку при сериализации в JSON

class PostSchema(PostBaseSchema, DatetimeFormatterMixin):
    """
    Cхема для записей
    """
    created_at: datetime | None = None
    updated_at: datetime | None = None

# Схема для обновления записи (patch-запрос, поля не обязательные)
PostInOptionalSchema = PostSchema.all_optional('PostInOptionalSchema')

class PostOutSchema(BaseOutSchema, PostSchema):
    """
    Схема для вывода поста (с id автора)
    """
    user: str  # Вывод вложенной модели с одним полем id пользователя

class PostOutWithAuthorSchema(PostOutSchema):
    """
    Схема для вывода поста (со всеми данными автора)
    """
    user: UserOutSchema  # Вывод вложенной модели со всеми полями пользователя

class ListPostResponse(BaseModel):
    """
    Схема для вывода списка постов
    """
    status: str
    results: int
    posts: List[PostOutSchema]

class ListPostWithAuthorsResponse(BaseModel):
    """
    Схема для вывода списка постов с данными об авторе
    """
    status: str
    results: int
    posts: List[PostOutWithAuthorSchema]
