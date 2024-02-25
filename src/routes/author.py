from datetime import datetime

from bson import ObjectId
from fastapi import Depends, status, HTTPException, Response
from loguru import logger
from pymongo import ReturnDocument

from src.database import Post
from src.routes.base import APIBaseRouter
from src.schemas.post import ListPostResponse, PostOutSchema, PostSchema, PostInOptionalSchema
from src.serializers.post import post_list_entity, post_entity
from src.utils.check_authorization import require_user


router = APIBaseRouter(tags=['Post author'])

@router.get(
    '/author/posts',
    response_model=ListPostResponse,
)
async def get_posts(
        limit: int = 10,
        page: int = 1,
        search: str = '',
        user_id: str = Depends(require_user)
):
    """
    Вывод постов текущего пользователя
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
    results = await results.to_list(length=None)
    posts = await post_list_entity(results)

    return {'status': 'success', 'results': len(posts), 'posts': posts}

@router.post(
    '/author/posts',
    status_code=status.HTTP_201_CREATED,
    response_model=PostOutSchema
)
async def create_post(
        post: PostSchema,
        user_id: str = Depends(require_user)
):
    """
    Добавление записи
    """

    post.created_at = datetime.utcnow()
    post.updated_at = post.created_at

    post_dict = post.dict()
    post_dict['user'] = ObjectId(user_id)

    result = await Post.insert_one(post_dict)
    post_db = await Post.find_one({'_id': result.inserted_id})
    new_post = await post_entity(post_db)

    return new_post

@router.get(
    '/author/posts/{post_id}',
    status_code=status.HTTP_200_OK,
    response_model=PostOutSchema
)
async def get_post(
        post_id: str,
        user_id: str = Depends(require_user)
):
    """
    Вывод записи автором по id поста
    """

    # Проверка корректности UUID (id) записи
    if not ObjectId.is_valid(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный номер записи: {post_id}"
        )

    # Фильтрация по id автора и записи
    query = {
        '$and': [
            {'_id': ObjectId(post_id)},
            {'user': ObjectId(user_id)}
        ]
    }

    post_db = await Post.find_one(query)

    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись №{post_id} не найдена"
        )

    post = await post_entity(post_db)

    return post

@router.patch(
    '/author/posts/{post_id}',
    status_code=status.HTTP_200_OK,
    response_model=PostOutSchema
)
async def update_post(
        post_id: str,
        post: PostInOptionalSchema,
        user_id: str = Depends(require_user)
):
    """
    Обновление поста автором
    """

    # Проверка корректности UUID (id) записи
    if not ObjectId.is_valid(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный номер записи: {post_id}"
        )

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

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Запись №{post_id} не найдена'
        )

    return await post_entity(updated_post)

@router.delete(
    '/author/posts/{post_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_post(
        post_id: str,
        user_id: str = Depends(require_user)
):
    """
    Удаление поста автором
    """

    if not ObjectId.is_valid(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный номер записи: : {post_id}"
        )

    # Поиск записи по id автора и поста
    filter_criteria = {
        "$and": [
            {'user': ObjectId(user_id)},
            {'_id': ObjectId(post_id)}
        ]
    }

    # find_one_and_delete находит и удаляет, возвращая удаляемый документ, если запись не найдено - вернет None
    post = await Post.find_one_and_delete(filter_criteria)

    logger.debug(f'post: {post}')

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Запись №{post_id} не найдена'
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
