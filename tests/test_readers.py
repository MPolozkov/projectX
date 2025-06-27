import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from patres.database import Base, get_db

from dotenv import load_dotenv

import os

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


@pytest.fixture
def auth_token(client: TestClient):
    """Получение токена при авторизации"""
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    response_json = response.json()
    assert "access_token" in response_json
    return response_json["access_token"]


# Создаем тестового читателя
def test_register_readers(client: TestClient, test_db):
    """Успешная регистрация читателя"""
    readers_data = {"name": "Алексей", "surname": "Ноговин", "patronymic": "Николаевич", "email": "user@yandex.ru"}
    response = client.post(
        "/readers",
        json=readers_data)
    assert response.status_code == 200
    assert response.json()["detail"] == "Читатель успешно зарегистрирован"


def test_login_success_readers(client: TestClient, reader_email="user@yandex.ru"):
    """Успешный запрос читателя"""
    response = client.get(
        f"/reader/{reader_email}"
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Читатель успешно зарегистрирован"


def test_login_no_success_readers(client: TestClient, reader_email="user145@yandex.ru"):
    """Не успешный запрос читателя"""
    response = client.get(
        f"/reader/{reader_email}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Такого читателя не существует"


def test_get_reader_success(client: TestClient, auth_token):
    """Успешное получение читателя с валидным токеном"""
    response = client.get(
        "/readers/",
        headers={"token": auth_token},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Запрос на всех читателей прошел успешно"


def test_reader_update_success(client: TestClient, auth_token, reader_email="user@yandex.ru"):
    readers_data = {"name": "Николай", "surname": "Ветров", "patronymic": "Алексеевич", "email": "luser@yandex.ru"}
    response = client.put(
        f"/readers/{reader_email}",
        headers={"token": auth_token},
        json=readers_data
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Введенный пользователь успешно изменен"


def test_reader_delete(client: TestClient, auth_token, reader_email="luser@yandex.ru"):
    response = client.delete(
        f"/readers/{reader_email}",
        headers={"token": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Пользователь удален"
