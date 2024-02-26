from typing import Dict, List

from src.database import Post
from src.repositories.post import PostRepository
from src.serializers.post import post_list_all_entity


class PostService:
    """
    Вывод и сериализация постов любым пользователем
    """

    @classmethod
    async def get_list(
            cls,
            limit: int,
            page: int,
            search: str
    ) -> List[Dict]:
        """
        Возврат списка постов
        :param limit: кол-во выводимых записей на странице
        :param page: номер текущей страницы
        :param search: фраза для фильтрации записей
        :return: список с записями
        """

        posts_list = await PostRepository.get_list(search=search, page=page, limit=limit)
        posts = await post_list_all_entity(posts_list)

        return posts

    @classmethod
    async def get(cls, post_id: str) -> List[Post]:
        """
        Возврат записи по id
        :param post_id: id поста
        :return: список с результатом
        """

        result = await PostRepository.get_with_author_data(post_id=post_id)
        post = await post_list_all_entity(result)

        return post
