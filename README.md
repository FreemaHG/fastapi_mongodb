# RESTful API на FastAPI с MongoDB

Проект представляет собой API с возможностью регистрации и авторизации пользователя. 
Публиковать посты могут только авторизованные пользователи. Просмотр и редактирование только своих постов.
Написан на фреймворке FastAPI с использованием MongoDB в качестве основной БД.

## Инструменты
* **Python** (3.11);
* **FastAPI** (asynchronous Web Framework);
* **MongoDB** (database);
* **Pydantic** (data verification);
* **Docker Compose**.

## Сборка

1. Скачиваем содержимое репозитория в отдельную папку:
    ```
    git clone https://github.com/FreemaHG/fastapi_mongodb.git
    ```
   
2. Переименовываем файл "**.env.template**" в "**.env**".


3. Собираем и запускаем контейнер с БД:
   ```
   docker-compose up -d
   ```
   
4. Остановка и удаление контейнеров:
   ```
   docker-compose down
   ```