from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    """
    Хэширование паролей в виде обычного текста
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверка пароля с его хэшем
    """
    return pwd_context.verify(password, hashed_password)
