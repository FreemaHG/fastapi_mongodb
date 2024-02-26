from typing import List, Dict, Optional

from bson import ObjectId
from pymongo import ReturnDocument

from src.database import Post
from src.schemas.post import PostInOptionalSchema


class AuthorRepository:
    """
    Вывод своих постов, добавление, обновление и удаление постов из БД автором
    """

    @classmethod
    async def get_list(
            cls,
            limit: int,
            page: int,
            search: str,
            user_id: str
    ) -> List[Post]:
        """
        Возврат из БД списка постов автора
        :param limit: кол-во записей на странице
        :param page: номер страницы
        :param search: фраза для фильтрации
        :param user_id: id автора
        :return: список с постами
        """

        # Фильтрация по автору и частичному совпадению в title или content (без учета регистра)
        filter_criteria = {
            "$and": [
                {'user': ObjectId(user_id)},
                {"$or": [
                    {"title": {"$regex": f'.*{search}.*', "$options": "i"}},
                    {"content": {"$regex": f'.*{search}.*', "$options": "i"}},
                ]}
            ]
        }

        # Пагинация и сортировка по дате (сначала новые)
        results = Post.find(filter_criteria).sort([("updated_at", -1)]).skip((page - 1) * limit).limit(limit)
        posts_list = await results.to_list(length=None)

        return posts_list

    @classmethod
    async def get(cls, post_id: str, user_id: str) -> Post:
        """
        Возврат записи из БД по id поста и автора
        :param post_id: id записи
        :param user_id: id автора
        :return: объект записи
        """

        # Фильтрация по id автора и записи
        query = {
            '$and': [
                {'_id': ObjectId(post_id)},
                {'user': ObjectId(user_id)}
            ]
        }

        post = await Post.find_one(query)

        return post

    @classmethod
    async def create(cls, post_data: Dict):
        """
        Добавление в БД новой записи
        :param post_data: словарь с данными
        :return: объект новой записи
        """

        result = await Post.insert_one(post_data)

        return result

    @classmethod
    async def update(
            cls,
            post_id: str,
            user_id: str,
            post: PostInOptionalSchema
    ) -> Optional[Post]:
        """
        Обновление поста в БД автором по id записи
        :param post_id: id записи
        :param user_id: id автора
        :param post: новые данные записи
        :return: объект обновленной записи | None
        """

        # Поиск записи по id автора и поста
        filter_criteria = {
            "$and": [
                {'user': ObjectId(user_id)},
                {'_id': ObjectId(post_id)}
            ]
        }

        # Поиск и обновление записи
        # ReturnDocument.AFTER - возврат обновленной записи
        # Если записи нет - вернет None
        updated_post = await Post.find_one_and_update(
            filter_criteria,
            {'$set': post.dict(exclude_none=True)},
            return_document=ReturnDocument.AFTER
        )

        return updated_post

    @classmethod
    async def delete(
            cls,
            post_id: str,
            user_id: str
    ) -> Optional[Post]:
        """
        Удаление из БД автором записи по id поста
        :param post_id: id записи
        :param user_id: id автора
        :return: объект удаленной записи | None
        """

        # Поиск записи по id автора и поста
        filter_criteria = {
            "$and": [
                {'user': ObjectId(user_id)},
                {'_id': ObjectId(post_id)}
            ]
        }

        # find_one_and_delete находит и удаляет, возвращая удаляемый документ, если запись не найдено - вернет None
        post = await Post.find_one_and_delete(filter_criteria)

        return post
