from pydantic import BaseModel


class BaseOutSchema(BaseModel):
    """
    Базовая схема для вывода данных из БД
    """
    id: str
