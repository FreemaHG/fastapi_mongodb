from datetime import datetime

from pydantic import BaseModel, validator


class DatetimeFormatterMixin(BaseModel):
    """
    Схема для преобразования даты создания и обновления в нужном формате
    """

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @validator('created_at')
    def serialize_created_at(cls, post_datetime: datetime):
        """
        Возвращаем дату и время создания поста в нужном формате
        """
        formatted_datetime = post_datetime.strftime("%d-%m-%Y %H:%M:%S")

        return formatted_datetime

    @validator('updated_at')
    def serialize_updated_at(cls, post_datetime: datetime):
        """
        Возвращаем дату и время обновления поста в нужном формате
        """
        formatted_datetime = post_datetime.strftime("%d-%m-%Y %H:%M:%S")

        return formatted_datetime
