# Импортируем FastApi зависимости
from fastapi import FastAPI

# Импортируем SQLAlchemy для работы с бд
from sqlalchemy import create_engine

# Импортируем базовый класс для моделей
from sqlalchemy.orm import declarative_base

# Импортируем сессию для работы с бд.
from sqlalchemy.orm import sessionmaker


# Создаем объект FastApi
app = FastAPI()

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

# Создаем базовый класс для моделей, чтобы все модели могли наследоваться от него
Base = declarative_base()


# Вставляем модель таблицы для создания ее в бд


    # __table_args__ = {'extend_existing': True}


# Удаляем и пересоздаем таблицы
# try:
    # Base.metadata.drop_all(bind=engine)  # Удаляем только таблицу Reader
    # Base.metadata.create_all(bind=engine)
    # print("Таблица BorrowedBook успешно пересоздана.")
# except Exception as e:
    # print(f"Ошибка при пересоздании таблицы BorrowedBook: {e}")


# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()  # Создаем новую сессию
    try:
        yield db  # Возвращаем сессию для использования
    finally:
        db.close()  # Закрываем сессию после использования
