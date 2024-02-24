from fastapi import Depends

from src.routes.base import APIBaseRouter
from src.schemas.user import UserResponseSchema
from src.services.user import UserService
from src.utils.check_authorization import require_user


router = APIBaseRouter(tags=['User'])

@router.get('/users/me', response_model=UserResponseSchema)
async def get_me(user_id: int = Depends(require_user)):
    """
    Вывод данных о текущем пользователе
    """

    user_data = await UserService.get(user_id=user_id)

    return {"status": "success", "user": user_data}
