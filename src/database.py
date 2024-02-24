import pymongo
from pymongo import mongo_client
from loguru import logger

from src.config import settings


client = mongo_client.MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    logger.debug(f'Подключение к MongoDB: {conn.get("version")}')
except Exception:
    logger.error('Не удается подключиться к MongoDB')

db = client[settings.MONGO_INITDB_DATABASE]  # Создаем БД
User = db.users  #  Сздаем коллекцию (таблицу) users
User.create_index([('email', pymongo.ASCENDING)], unigue=True)  # Индексируем поле email, проверка на уникальность
