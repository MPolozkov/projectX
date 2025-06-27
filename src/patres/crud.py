from typing import Optional, List, Type

from sqlalchemy.orm import Session
from patres import schemas, models, security
from fastapi import HTTPException

from patres.models import Reader, Book


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Функция для создания нового библиотекаря"""
    db_user = models.User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    raise HTTPException(status_code=200, detail="Библиотекарь создан")
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Функция для проверки библиотекаря по email при регистрации"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    return user


def get_user_by_email_login(db: Session, email: str, password: str) -> Type[models.User]:
    """Функция для проверки библиотекаря по email при входе"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Такого пользователя не существует пройдите регистрацию")
    return user


def create_book(db: Session, book: schemas.BookCreate) -> models.Book:
    """Функция для создания новой книги"""
    db_book = models.Book(**book.dict())  # Создаем новый объект книги, используя данные из схемы
    db.add(db_book)  # Добавляем книгу в сессию
    db.commit()  # Сохраняем изменения в базе данных
    db.refresh(db_book)  # Обновляем объект книги, чтобы получить его ID и другие данные из БД
    raise HTTPException(status_code=200, detail="Книга успешно создана")
    return db_book  # Возвращаем созданную книгу


def get_book_by_title(db: Session, book_title: str) -> Optional[models.Book]:
    """Функция для обновления книги"""
    book_title = db.query(models.Book).filter(models.Book.title == book_title).first()
    if not book_title:
        raise HTTPException(status_code=400, detail="Книга не найдена")

    return book_title

def get_book_update(db: Session, book_title: str, book_update: schemas.BookUpdate) -> models.Book:
    book = get_book_by_title(db, book_title)

    for field, value in book_update.dict(exclude_defaults=True).items():
        setattr(book, field, value)

    db.add(book)
    db.commit()
    db.refresh(book)
    raise HTTPException(status_code=200, detail="Введенная книга успешно изменена")
    return book


def get_book_by_title_delete(db: Session, book_title: str) -> Optional[models.Book]:
    """Функция для удаления книги"""
    book_title = db.query(models.Book).filter(models.Book.title == book_title).first()
    if not book_title:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    db.delete(book_title)
    db.commit()
    raise HTTPException(status_code=200, detail="Книга удалена")
    return book_title


def get_book_by_bd(db: Session, db_book: schemas.Book) -> models.Book:
    """Функция для обновления книги в бд"""
    db.add(db_book)  # Добавляем изменения в сессию
    db.commit()  # Фиксируем изменения в БД
    db.refresh(db_book)  # Обновляем объект книги из БД
    return db_book  # Возвращаем обновленную книгу


def get_books(db: Session) -> list[Type[Book]]:
    """Функция для получения списка всех книг"""
    get_books = db.query(models.Book).all()
    raise HTTPException(status_code=200, detail="Запрос на ве книги успешен")
    return get_books



def create_readers(db: Session, reader: schemas.ReaderCreate) -> models.Reader:
    """Регистрация читателя"""
    db_reader = models.Reader(
        name=reader.name, surname=reader.surname, patronymic=reader.patronymic, email=reader.email
    )
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    raise HTTPException(status_code=200, detail="Читатель успешно зарегистрирован")
    return db_reader


def get_reader(db: Session) -> list[Type[Reader]]:
    """Функция для получения всех читателей"""
    readers_get = db.query(models.Reader).all()
    raise HTTPException(status_code=200, detail="Запрос на всех читателей прошел успешно")
    return readers_get


def get_reader_by_email(db: Session, email: str) -> Optional[models.Reader]:
    """Проверка читателя по email"""
    db_reader = db.query(models.Reader).filter(models.Reader.email == email).first()
    if db_reader:
        raise HTTPException(status_code=400, detail="Такой читатель уже существует")
    return db_reader


def get_reader_by_one(db: Session, reader_email: str) -> Optional[models.Reader]:
    """Получение читателя по email"""
    get_reader = db.query(models.Reader).filter(models.Reader.email == reader_email).first()
    if not get_reader:
        raise HTTPException(status_code=404, detail="Такого читателя не существует")
    raise HTTPException(status_code=200, detail="Читатель успешно зарегистрирован")
    return get_reader


def get_reader_by_update(db: Session, reader_email: str) -> Optional[models.Reader]:
    """Функция для обновления читателя"""
    reader_email = db.query(models.Reader).filter(models.Reader.email == reader_email).first()
    if not reader_email:
        raise HTTPException(status_code=404, detail="Такого пользователя не существует проверьте введенные данные")
    return reader_email


def get_reader_by_bd(db: Session, reader_email: str, reader_update: schemas.ReaderUpdate) -> models.Reader:
    """Функция для изменения читателя в бд"""
    reader = get_reader_by_update(db, reader_email)

    for field, value in reader_update.dict(exclude_defaults=True).items():
        setattr(reader, field, value)

    db.add(reader)
    db.commit()
    db.refresh(reader)
    raise HTTPException(status_code=200, detail="Введенный пользователь успешно изменен")
    return reader


def readers_delete(db: Session, reader_email: str) -> Optional[models.Reader]:
    db_reader = db.query(models.Reader).filter(models.Reader.email == reader_email).first()
    if not db_reader:
        raise HTTPException(status_code=404, detail="Такой читатель не найден")
    db.delete(db_reader)
    db.commit()
    raise HTTPException(status_code=200, detail= "Пользователь удален")
    return db_reader
