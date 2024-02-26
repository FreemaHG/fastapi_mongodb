from bson import ObjectId
from fastapi import Depends, status, HTTPException, Response

from src.routes.base import APIBaseRouter
from src.schemas.post import ListPostResponse, PostOutSchema, PostSchema, PostInOptionalSchema
from src.services.author import AuthorService
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

    posts = await AuthorService.get_list(limit=limit, page=page, search=search, user_id=user_id)

    return {
        'status': 'success',
        'results': len(posts),
        'posts': posts
    }

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
    new_post = await AuthorService.create(user_id=user_id, post=post)

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

    post = await AuthorService.get(post_id=post_id, user_id=user_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись №{post_id} не найдена"
        )

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

    updated_post = await AuthorService.update(post_id=post_id, user_id=user_id, post=post)

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Запись №{post_id} не найдена'
        )

    return updated_post

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

    deleted_post = await AuthorService.delete(post_id=post_id, user_id=user_id)

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Запись №{post_id} не найдена'
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
