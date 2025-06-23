import pytest
from fastapi.testclient import TestClient

from patres import crud

# Импортируем FastApi зависимости
from fastapi import FastAPI

# Импортируем SQLAlchemy для работы с бд
from sqlalchemy import create_engine

# Импортируем базовый класс для моделей
from sqlalchemy.orm import declarative_base

# Импортируем сессию для работы с бд.
from sqlalchemy.orm import sessionmaker

from patres.database import Base, get_db, app

user = "postgres"
password = "123"
host = "localhost"
database = "postgres"

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
        for table in reversed(Base.metadata.sorted_tables):
            engine.execute(table.delete())
        db.close()


# Фикстура для клиента FastAPI  переопределением зависимостей
@pytest.fixture()
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.depedency_overrides[get_db] = override_get_db()
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_register_user(client: TestClient, test_db):
    user_data = {"email": "test@example.com", "password": "pssword123"}
    response = client.post("/register")
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    users = crud.get_user_by_email(db=test_db, email=user_data["email"])
    assert not users


# Тест регистрации пользователя с дублирующимся email
def test_register_user_duplicate_email(client: TestClient):
    user_data = {"email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)  # Регистрируем пользователя первый раз
    response = client.post("/register", json=user_data)  # Пытаемся зарегистрировать снова
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
