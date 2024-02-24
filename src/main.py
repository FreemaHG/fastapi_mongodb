from fastapi import FastAPI

from src.urls import register_routers


app = FastAPI()

register_routers(app)  # Регистрация URL
