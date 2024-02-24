
# Поскольку MongoDB использует документы BSON, создадим несколько сериализаторов,
# чтобы преобразовать их в словари Python.

def user_entity(user) -> dict:
    """
    Преобразовываем объект пользователя из БД в словарь
    :param user: объект пользователя
    :return: словарь с данными пользователя
    """
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "verified": user["verified"],
        "password": user["password"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }

def user_response_entity(user) -> dict:
    """
    Преобразовываем ответ с данными пользователя в словарь
    """
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }

def embedded_user_response(user) -> dict:
    """
    Возвращаем словарь с основными данными пользователя
    """
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "photo": user["photo"]
    }


def user_list_entity(users) -> list:
    """
    Возвращаем список с данными пользователей
    """
    return [user_entity(user) for user in users]
