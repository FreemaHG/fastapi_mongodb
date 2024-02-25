from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

from src.schemas.base import BaseOutSchema
from src.schemas.mixin import DatetimeFormatterMixin


class UserBaseSchema(BaseModel):
    """
    Базовая схема для пользователей
    """
    name: str
    email: EmailStr
    photo: str | None = None
    role: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class CreateUserSchema(UserBaseSchema):
    """
    Схема для создания нового пользователя
    """
    password: constr(min_length=8)
    password_confirm: str
    verified: bool = False

class LoginUserSchema(BaseModel):
    """
    Схема для входа пользователя
    """
    email: EmailStr
    password: constr(min_length=8)

class UserOutSchema(BaseOutSchema, UserBaseSchema, DatetimeFormatterMixin):
    """
    Схема для вывода данных о пользователе
    """
    pass

class UserResponseSchema(BaseModel):
    """
    Схема для вывода ответа после создания пользователя
    """
    status: str
    user: UserOutSchema
