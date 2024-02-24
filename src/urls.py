from fastapi import FastAPI

from src.routes.auth import router as auth_router
from src.routes.user import router as user_router


def register_routers(app: FastAPI) -> FastAPI:
    """
    Регистрация роутов для API
    """

    app.include_router(auth_router)
    app.include_router(user_router)

    return app
