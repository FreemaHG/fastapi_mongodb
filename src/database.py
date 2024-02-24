import pymongo
from motor import motor_asyncio
from loguru import logger

from src.config import settings

# Асинхронное подключение к БД
client = motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    logger.debug('Подключение к MongoDB')

except Exception:
    logger.error('Не удается подключиться к MongoDB')

db = client[settings.MONGO_INITDB_DATABASE]  # Создаем БД
User = db.users  #  Сздаем коллекцию (таблицу) users
User.create_index([('email', pymongo.ASCENDING)])  # Индексируем поле email
