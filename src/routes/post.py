from fastapi import HTTPException, status
from bson.objectid import ObjectId

from src.routes.base import APIBaseRouter
from src.schemas.post import (
    PostOutWithAuthorSchema, ListPostWithAuthorsResponse
)
from src.services.post import PostService


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

    posts = await PostService.get_list(search=search, page=page, limit=limit)

    return {
        'status': 'success',
        'results': len(posts),
        'posts': posts
    }

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

    posts = await PostService.get(post_id=post_id)

    if len(posts) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись №{post_id} не найдена"
        )

    return posts[0]
