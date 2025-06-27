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


def test_borrow_book(client: TestClient, auth_token, book_title="Басни", reader_email="pipl82308@gmail.com"):
    """Успешная выдача книги"""
    response = client.post(
        f"/borrowed_book/{book_title}/{reader_email}",
        headers={"token": auth_token},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Книга выдана"


def test_return_book(client: TestClient, auth_token, book_title="Басни", reader_email="pipl82308@gmail.com"):
    response = client.post(
        f"/return_book/{book_title}/{reader_email}",
        headers={"token": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Книга возвращена"
