from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from src.database import Post
from src.repositories.author import AuthorRepository
from src.repositories.post import PostRepository
from src.schemas.post import PostSchema, PostInOptionalSchema
from src.serializers.post import post_list_entity, post_entity


class AuthorService:
    """
    Вывод постов, добавление, обновление и удаление постов автором
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
        Возврат списка постов автора
        :param limit: кол-во записей на странице
        :param page: номер страницы
        :param search: фраза для фильтрации
        :param user_id: id автора
        :return: список с постами
        """

        posts_list = await AuthorRepository.get_list(limit=limit, page=page, search=search, user_id=user_id)
        posts = await post_list_entity(posts_list)

        return posts

    @classmethod
    async def get(
            cls,
            post_id: str,
            user_id: str
    ) -> Optional[Post]:
        """
        Возврат записи по id поста и автора
        :param post_id: id записи
        :param user_id: id автора
        :return: объект записи
        """

        post_db = await AuthorRepository.get(post_id=post_id, user_id=user_id)

        if post_db:
            return await post_entity(post_db)

        return None

    @classmethod
    async def create(
            cls,
            post: PostSchema,
            user_id: str) -> Post:
        """
        Добавление записи автором
        :param post: данные новой записи
        :param user_id: id автора
        :return: объект созданной записи
        """

        post.created_at = datetime.utcnow()
        post.updated_at = post.created_at

        post_dict = post.dict()
        post_dict['user'] = ObjectId(user_id)

        created_post = await AuthorRepository.create(post_data=post_dict)
        post_db = await PostRepository.get_for_id(post_id=created_post.inserted_id)
        new_post = await post_entity(post_db)

        return new_post

    @classmethod
    async def update(
            cls,
            post_id: str,
            post: PostInOptionalSchema,
            user_id: str
    ) -> Optional[Post]:
        """
        Обновление поста автором по id записи
        :param post_id: id записи
        :param user_id: id автора
        :param post: новые данные записи
        :return: словарь с данными обновленной записи | None
        """

        updated_post = await AuthorRepository.update(post_id=post_id, user_id=user_id, post=post)

        if updated_post:
            updated_post_dict = await post_entity(updated_post)

            return updated_post_dict

        return None

    @classmethod
    async def delete(
            cls,
            post_id: str,
            user_id: str
    ) -> Optional[Post]:
        """
        Удаление автором записи по id поста
        :param post_id: id записи
        :param user_id: id автора
        :return: объект удаленной записи | None
        """

        deleted_post = await AuthorRepository.delete(post_id=post_id, user_id=user_id)

        return deleted_post
