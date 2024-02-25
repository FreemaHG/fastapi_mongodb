from fastapi import FastAPI

from src.routes.auth import router as auth_router
from src.routes.user import router as user_router
from src.routes.post import router as post_router
from src.routes.author import router as author_router



def register_routers(app: FastAPI) -> FastAPI:
    """
    Регистрация роутов для API
    """

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(post_router)
    app.include_router(author_router)

    return app
