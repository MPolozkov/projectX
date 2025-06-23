from sqlalchemy import Column, Integer, String, DateTime

from .database import Base


# Модель для создания нового библиотекаря
class User(Base):
    __tablename__ = "users"  # Указываем название таблицы в бд

    id = Column(Integer, primary_key=True, index=True)  # Поле id, является первичным ключом и индексируется
    email = Column(String, unique=True, index=True)  # Поле email, уникально и индексируется
    hashed_password = Column(String)  # Поле для хранения хэшированного пароля


# Модель для создания новой книги
class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Название книги не может быть пустым
    author = Column(String, nullable=False)
    year_of_publication = Column(Integer, nullable=True)
    isbn = Column(String, unique=True, nullable=True)  # ISBN книги, уникально и может быть пустым
    copies = Column(Integer, default=1)  # Количество копий книги, по умолчанию 1


# Модель для создания нового читателя
class Reader(Base):
    __tablename__ = 'readers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)


# Модель для записи какой читатель какую книгу взял
class BorrowedBook(Base):
    __tablename__ = "borrowed_books"  # Название таблицы для заимствованных книг

    id = Column(Integer, primary_key=True, index=True)
    book_title = Column(String)  # Ссылка на книгу, используем внешние ключи
    reader_email = Column(String)  # Ссылка на читателя
    borrow_date = Column(DateTime)  # Дата заимствования книги
    return_date = Column(DateTime)  # Дата возврата книги, не может быть пустой
