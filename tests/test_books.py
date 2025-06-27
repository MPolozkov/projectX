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


@pytest.fixture
def auth_token(client: TestClient):
    """Получение токена при авторизации"""
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    response_json = response.json()
    assert "access_token" in response_json
    return response_json["access_token"]


invalid_token = "ygofiweefjedhfvp[ahp[fgpd;eoerhopguhedofgve[dgoijheeobv]]]"


# Тесты для создания новой книги
def test_create_book_success(client: TestClient, auth_token):
    """Тест когда токен получен"""
    response = client.post(
        "/books/",
        headers={"token": auth_token},
        json={"title": "Рассказы", "author": "Пушкин", "year_of_publication": 2789, "isbn": "8906", "copies": 6},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Книга успешно создана"


def test_create_book_no_token(client: TestClient):
    """Создание тестовой книги когда нет токена."""
    response = client.post(
        "/books/",
        headers={"token": ""},
        json={"title": "Сказки", "author": "Лермонтов", "year_of_publication": 1894, "isbn": "874", "copies": 3}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Требуется аутентификация"


def test_create_book_invalid_token(client: TestClient):
    """"Создание тестовой книги с недопустимым токеном"""
    response = client.post(
        "/books/",
        headers={"token": invalid_token},  # Используем неверный токен
        json={"title": "Сказки", "author": "Чуковский", "year_of_publication": 1989, "isbn": "12345", "copies": 10},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Неверный токен"


# Получение всех книг
def test_read_books_get(client: TestClient, auth_token):
    """"Тест с валидным токеном для получения всех книг"""
    response = client.get(
        "/books/",
        headers={"token": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Запрос на ве книги успешен"


def test_read_books_get_no_token(client: TestClient):
    """Тест на запрос всех книг без токена"""
    response = client.get(
        "/books/",
        headers={"token": ""},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Требуется аутентификация"


def test_reader_update_success(client: TestClient, auth_token, book_title="Рассказы"):
    """Тест для изменения книги"""
    readers_data = {"title": "Басни",
                    "author": "Толстов",
                    "year_of_publication": 1478,
                    "isbn": "8734",
                    "copies": 4
                    }
    response = client.put(
        f"/books/{book_title}",
        headers={"token": auth_token},
        json=readers_data
    )
    assert response.status_code == 200
    assert response.json()['detail'] == "Введенная книга успешно изменена"


# Тесты для получения одной книги по названию
def test_read_books_one_valid_token(client: TestClient, auth_token, book_title="Рассказы"):
    """Тест с валидным токеном."""
    response = client.get(
        f"/books/{book_title}",
        headers={"token": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Книга получена"


def test_read_books_one_no_invalid_token(client: TestClient, auth_token, book_title="Рассказы"):
    """Тест с не валидным токеном."""
    response = client.get(
        f"/books/{book_title}",
        headers={"token": invalid_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный токен"


def test_read_books_one_no_token(client: TestClient, auth_token, book_title="Рассказы"):
    """Тест с нет токена."""
    response = client.get(
        f"/books/{book_title}",
        headers={"token": ""}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Требуется аутентификация"


def test_read_books_one_no_title(client: TestClient, auth_token, book_title="Сказки"):
    """Тест если нет книги."""
    response = client.get(
        f"/books/{book_title}",
        headers={"token": auth_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"


# Тесты для удаления книги
def test_delete_valid_token(client: TestClient, auth_token, book_title="Рассказы"):
    """Тест удаление книги с валидным токеном."""
    response = client.delete(
        f"/delete/{book_title}",
        headers={"token": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Книга удалена"


def test_delete_invalid_token(client: TestClient, book_title="Рассказы"):
    """Тест удаление книги с не валидным токеном."""
    response = client.delete(
        f"/delete/{book_title}",
        headers={"token": invalid_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный токен"


def test_delete_no_token(client: TestClient, book_title="Рассказы"):
    """Тест удаление книги нет токеном."""
    response = client.delete(
        f"/delete/{book_title}",
        headers={"token": ""}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Требуется аутентификация"


def test_delete_no_book(client: TestClient, auth_token, book_title="Басни"):
    """Тест удаление книги нет книги."""
    response = client.delete(
        f"/delete/{book_title}",
        headers={"token": auth_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"
