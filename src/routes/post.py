from fastapi import HTTPException, status
from bson.objectid import ObjectId

from src.routes.base import APIBaseRouter
from src.schemas.post import (
    PostOutWithAuthorSchema, ListPostWithAuthorsResponse
)
from src.database import Post
from src.serializers.post import post_list_all_entity


router = APIBaseRouter(tags=['Post guest'])

@router.get(
    '/posts',
    response_model=ListPostWithAuthorsResponse,
)
async def get_posts(
        limit: int = 10,
        page: int = 1,
        search: str = '',
):
    """
    Вывод всех постов (с данными авторов)
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

    results = await Post.aggregate(pipeline).to_list(length=None)
    posts = await post_list_all_entity(results)

    return {'status': 'success', 'results': len(posts), 'posts': posts}

@router.get(
    '/posts/{post_id}',
    status_code=status.HTTP_200_OK,
    response_model=PostOutWithAuthorSchema
)
async def get_post(
        post_id: str,
):
    """
    Вывод записи по id (с данными автора)
    """

    # Проверка корректности UUID (id) записи
    if not ObjectId.is_valid(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный номер записи: {post_id}"
        )

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

    results = await Post.aggregate(pipeline).to_list(length=None)

    if len(results) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись №{post_id} не найдена"
        )

    post = await post_list_all_entity(results)

    return post[0]
