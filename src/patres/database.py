# Импортируем FastApi зависимости
import os

from fastapi import FastAPI

# Импортируем SQLAlchemy для работы с бд
from sqlalchemy import create_engine

# Импортируем базовый класс для моделей
from sqlalchemy.orm import declarative_base

# Импортируем сессию для работы с бд.
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Создаем объект FastApi
app = FastAPI()

load_dotenv()

# имя пользователя в бд
user = os.getenv('user')

# Пароль бд
password = os.getenv('password')

# хост на котором работает бд
host = os.getenv('host')

# Имя бд
database = os.getenv('database')

# Строка подключения к базе данных PostgresSQL
DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}"

# Создаем движок для подключения к базе данных с указанной строкой подключения
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Создаем фабрику сессий, которая управляет сессиями с помощью движка
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей, чтобы все модели могли наследоваться от него
Base = declarative_base()


# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()  # Создаем новую сессию
    try:
        yield db  # Возвращаем сессию для использования
    finally:
        db.close()  # Закрываем сессию после использования
