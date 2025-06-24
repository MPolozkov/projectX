import os

import pytest
from fastapi.testclient import TestClient

from patres import crud, auth, schemas

# Импортируем FastApi зависимости
from fastapi import FastAPI

# Импортируем SQLAlchemy для работы с бд
from sqlalchemy import create_engine

# Импортируем базовый класс для моделей
from sqlalchemy.orm import declarative_base

# Импортируем сессию для работы с бд.
from sqlalchemy.orm import sessionmaker

from patres.database import Base, get_db, app

from dotenv import load_dotenv

load_dotenv()

user = os.getenv('postgres')
password = os.getenv('password')
host = os.getenv('localhost')
database = os.getenv('postgres')

# Строка подключения к базе данных PostgresSQL
DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}"

# Создаем движок для подключения к базе данных с указанной строкой подключения
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Создаем фабрику сессий, которая управляет сессиями с помощью движка
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Фикстура для тестовой сессии с бд
@pytest.fixture()
def test_db():
    # Создаем таблицы в бд если их еще нет
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        # Очищаем сессию и удаляем все данные из таблицы после каждого теста
        with engine.connect() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
        db.close()


# Фикстура для клиента FastAPI  переопределением зависимостей
@pytest.fixture()
def client(test_db):
    app.dependency_overrides = {}

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    app.dependency_overrides = {}


from main import app


# Создаем тестового пользователя
def test_register_user(client: TestClient, test_db):
    """Успешная регистрация"""
    user_data = {"email": "test@example.com", "password": "pssword123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


def test_register_user_duplicate_email(client: TestClient):
    """Тест регистрации пользователя с дублирующимся email"""
    user_data = {"email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)  # Регистрируем пользователя первый раз
    response = client.post("/register", json=user_data)  # Пытаемся зарегистрировать снова
    assert response.status_code == 404
    assert response.json()["detail"] == "Такой пользователь уже существует"


# Тест для входа пользователя
def test_login_success(client: TestClient, test_db):
    """Успешная авторизация"""
    # Подготавливаем данные для входа
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_email(client: TestClient, test_db):
    """Неверный email"""
    login_data = {"email": "wrong@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Неверный адрес электронной почты или пароль"


def test_login_incorrect_password(client: TestClient, test_db):
    login_data = {"email": "test@example@.com", "password": "pass123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Неверный адрес электронной почты или пароль"
