from typing import List
from bson.objectid import ObjectId

from src.database import Post


class PostRepository:
    """
    Вывод постов из БД любым пользователем
    """

    @classmethod
    async def get_list(
            cls,
            limit: int,
            page: int,
            search: str
    ) -> List[Post]:
        """
        Вывод из БД всех постов (с данными автора)
        :param limit: кол-во выводимых записей на странице
        :param page: номер текущей страницы
        :param search: фраза для фильтрации записей
        :return: список с записями
        """

        pipeline = [
            # Фильтрация
            {'$match': {
                # по частичному совпадению в title или content (без учета регистра)
                "$or": [
                    {"title": {"$regex": f'.*{search}.*', "$options": "i"}},
                    {"content": {"$regex": f'.*{search}.*', "$options": "i"}},
                ]
            }},
            # Запрос связанных данных автора (можно вывести данные автора в ответе)
            {'$lookup': {
                'from': 'users',
                'localField': 'user',
                'foreignField': '_id',
                'as': 'user'}
            },
            {'$unwind': '$user'},
            # Сортировка по дате (сначала новые)
            {"$sort": {"updated_at": -1}},
            # Пагинация
            {"$skip": (page - 1) * limit},
            {"$limit": limit}
        ]

        posts_list = await Post.aggregate(pipeline).to_list(length=None)

        return posts_list

    @classmethod
    async def get_for_id(cls, post_id: str) -> Post:
        """
        Возврат записи из БД по id
        :param post_id: id записи
        :return: объект записи
        """

        post = await Post.find_one({'_id': post_id})

        return post

    @classmethod
    async def get_with_author_data(cls, post_id: str) -> List[Post]:
        """
        Возврат записи из БД по id (с данными автора)
        :param post_id: id поста
        :return: список с результатом
        """

        pipeline = [
            # Фильтрация
            {'$match': {
                # Поиск по id записи
                "$and": [
                    {'_id': ObjectId(post_id)}
                ]
            }},
            # Запрос связанных данных автора (можно вывести данные автора в ответе)
            {'$lookup': {
                'from': 'users',
                'localField': 'user',
                'foreignField': '_id',
                'as': 'user'}
            },
            {'$unwind': '$user'},
        ]

        post = await Post.aggregate(pipeline).to_list(length=None)

        return post
