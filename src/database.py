import pymongo
from motor import motor_asyncio

from loguru import logger

from src.config import settings

# Асинхронное подключение к БД
client = motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)

try:
    conn = client.server_info()
    logger.debug('Подключение к MongoDB')

except Exception:
    logger.error('Не удается подключиться к MongoDB')

db = client[settings.MONGO_INITDB_DATABASE]  # Создаем БД`
User = db.users  #  Сздаем коллекцию (таблицу) users
Post = db.posts  #  Сздаем коллекцию (таблицу) posts
User.create_index([('email', pymongo.ASCENDING)])  # Индексируем поле email
User.create_index([('title', pymongo.ASCENDING)])  # Индексируем поле email
