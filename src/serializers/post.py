from typing import Dict, List

from src.serializers.user import user_response_entity


async def post_entity(post) -> Dict:
    """
    Сериализуем объект поста из БД в словарь
    """
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "category": post["category"],
        "content": post["content"],
        "image": post["image"],
        "user": str(post["user"]),
        "created_at": post["created_at"],
        "updated_at": post["updated_at"]
    }


async def populated_post_entity(post) -> Dict:
    """
    Сериализуем объект поста из БД в словарь с вложенными данными о пользователе
    """
    post_dict = await post_entity(post=post)
    post_dict['user'] = await user_response_entity(user=post['user'])

    return post_dict


async def post_list_entity(posts) -> List:
    """
    Сериализуем и возвращаем список постов
    :param posts:
    :return:
    """

    posts_list = [await post_entity(post) for post in posts]

    return posts_list

async def post_list_all_entity(posts) -> List:
    """
    Сериализуем и возвращаем список постов
    :param posts:
    :return:
    """

    posts_list = [await populated_post_entity(post) for post in posts]

    return posts_list
