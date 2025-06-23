from datetime import datetime, timedelta  # Импортируем модули для работы с временем
from jose import JWTError, jwt  # Импортируем библиотеку для работы с JWT
from passlib.context import CryptContext  # Импортируем контекст для хеширования паролей

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "your_secret_key"  # Секретный ключ для шифрования JWT
ALGORITHM = "HS256"  # Алгоритм для создания JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена в минутах

# Создаем контекст для хеширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plan_password, hashed_password):
    """Функция для проверки пароля"""
    return pwd_context.verify(plan_password, hashed_password)  # Возвращает True, если пароль совпадает


def get_password_hash(password):
    """Функция для хеширования пароля"""
    return pwd_context.hash(password)  # Возвращает хэшированный пароль


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Функция для создания токена доступа с заданными данными и временем жизни"""
    to_encode = data.copy()  # Копируем данные для токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Устанавливаем время истечения
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # По умолчанию
    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Шифруем токен
    return encoded_jwt  # Возвращаем закодированный токен




