import os
from datetime import datetime, timedelta  # Импортируем модули для работы с временем
from jose import JWTError, jwt  # Импортируем библиотеку для работы с JWT
from passlib.context import CryptContext  # Импортируем контекст для хеширования паролей
from fastapi import HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends


# Создаем контекст для хеширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plan_password, hashed_password):
    """Функция для проверки пароля"""
    return pwd_context.verify(plan_password, hashed_password)


def get_password_hash(password):
    """Функция для хеширования пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Функция для создания токена доступа с заданными данными и временем жизни"""
    to_encode = data.copy()  # Копируем данные для токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Устанавливаем время истечения
    else:
        expire = datetime.utcnow() + timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def decode_access_token(token: Optional[str] = Header(None), db: Session = None):
    if not token:
        raise HTTPException(status_code=404, detail="Требуется аутентификация")

    try:
        jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен")
    return token

