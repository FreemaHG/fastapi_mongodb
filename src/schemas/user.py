from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    """
    Базовая схема для пользователей
    """
    name: str
    email: EmailStr
    photo: str
    role: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

    # Автоматическое преобразование данных ORM-модели в объект схемы для сериализации
    # model_config = ConfigDict(from_attributes=True)

class CreateUserSchema(UserBaseSchema):
    """
    Схема для создания нового пользователя
    """
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False

class UserOutSchema(UserBaseSchema):
    """
    Схема для вывода данных о пользователе
    """
    id: str

class UserResponseSchema(BaseModel):
    """
    Схема для вывода ответа после создания пользователя
    """
    status: str
    user: UserOutSchema
