import os

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from patres.database import Base, get_db

from dotenv import load_dotenv

from main import app

load_dotenv()

user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
database = os.getenv('database')

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


# Создаем тестового пользователя
def test_register_user(client: TestClient, test_db):
    """Успешная регистрация"""
    user_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["detail"] == "Библиотекарь создан"


def test_register_user_duplicate_email(client: TestClient):
    """Тест регистрации пользователя с дублирующимся email"""
    user_data = {"email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)
    response = client.post("/register", json=user_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Такой пользователь уже существует"


# Тест для входа пользователя
def test_login_success(client: TestClient):
    """Успешная авторизация"""
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    # assert response.json()["token_type"] == "bearer"
    response_json = response.json()
    assert "access_token" in response_json
    assert response_json["token_type"] == "bearer"
    access_token = response_json["access_token"]
    assert access_token != ""


def test_login_incorrect_email(client: TestClient, test_db):
    """Неверный email"""
    login_data = {"email": "wrong@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Неверный адрес электронной почты"


def test_login_incorrect_password(client: TestClient, test_db):
    login_data = {"email": "test@example.com", "password": "pass123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Такого пользователя не существует пройдите регистрацию"
