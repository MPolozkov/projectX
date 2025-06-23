from sqlalchemy.orm import Session
from patres import schemas, models
from fastapi import HTTPException


def create_user(db: Session, user: schemas.UserCreate):
    """Функция для создания нового библиотекаря"""
    db_user = models.User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    """Функция для проверки библиотекаря по email при регистрации"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=404, detail="Такой пользователь уже существует")
    return user


def get_user_by_email_login(db: Session, email: str):
    """Функция для проверки библиотекаря по email при входе"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="Такого пользователя не существует пройдите регистрацию")


def create_book(db: Session, book: schemas.BookCreate):
    """Функция для создания новой книги"""
    db_book = models.Book(**book.dict())  # Создаем новый объект книги, используя данные из схемы
    db.add(db_book)  # Добавляем книгу в сессию
    db.commit()  # Сохраняем изменения в базе данных
    db.refresh(db_book)  # Обновляем объект книги, чтобы получить его ID и другие данные из БД
    return db_book  # Возвращаем созданную книгу


def get_book_by_title(db: Session, book_title: str):
    """Функция для обновления книги"""
    return db.query(models.Book).filter(models.Book.title == book_title).first()


def get_book_by_bd(db: Session, db_book: schemas.BookUpdate):
    """Функция для обновления книги в бд"""
    db.add(db_book)  # Добавляем изменения в сессию
    db.commit()  # Фиксируем изменения в БД
    db.refresh(db_book)  # Обновляем объект книги из БД
    return db_book  # Возвращаем обновленную книгу


def get_books(db: Session):
    """Функция для получения списка всех книг"""
    return db.query(models.Book).all()  # Возвращаем все книги из базы данных


def create_readers(db: Session, reader: schemas.ReaderCreate):
    """Регистрация читателя"""
    db_reader = models.Reader(name=reader.name,
                              surname=reader.surname,
                              patronymic=reader.patronymic,
                              email=reader.email)
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader


def get_reader(db: Session):
    """Функция для получения всех читателей"""
    return db.query(models.Reader).all()


def get_reader_by_email(db: Session, email: str):
    """Проверка читателя по email"""
    db_reader = db.query(models.Reader).filter(models.Reader.email == email).first()
    if db_reader:
        raise HTTPException(status_code=404, detail="Такой читатель уже существует")
    return db_reader


def get_reader_by_one(db: Session, reader_email: str):
    """Получение читателя по email"""
    return db.query(models.Reader).filter(models.Reader.email == reader_email).first()


def get_reader_by_update(db: Session, reader_email: str):
    """Функция для обновления читателя"""
    return db.query(models.Reader).filter(models.Reader.email == reader_email).first()


def get_reader_by_bd(db: Session, reader_update: schemas.ReaderCreate):
    """Функция для изменения читателя в бд"""
    db.add(reader_update)  # Добавляем изменения в сессию
    db.commit()  # Фиксируем изменения в БД
    db.refresh(reader_update)  # Обновляем объект книги из БД
    return reader_update  # Возвращаем обновленную книгу

