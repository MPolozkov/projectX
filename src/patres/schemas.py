# Импортируем базовую модель из Pydantic и тип EmailStr для валидации email
from pydantic import BaseModel, EmailStr


# Схема для создания нового пользователя
class UserCreate(BaseModel):
    email: EmailStr  # Поле для email, должен быть валидным адресом электронной почты
    password: str  # Поле для пароля


# Схема для представления пользователя в ответах API
class User(BaseModel):
    id: int  # Поле ID пользователя
    email: EmailStr  # Поле для email пользователя

    class Config:  # Конфигурация для модели
        from_attribute = True  # Включаем режим работы с ORM, чтобы Pydantic мог обрабатывать ORM-модели


# Схема для входа пользователя
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Схема для создания новой книги
class BookCreate(BaseModel):
    title: str  # Название книги
    author: str  # Для автора книги
    year_of_publication: int = None  # Поле для года публикации, по умолчанию None
    isbn: str = None  # Поле для ISBN, по умолчанию None
    copies: int = 1  # Поле для количества копий книги, по умолчанию 1


# Схема для представления книги в ответах API
class Book(BaseModel):
    id: int  # Поле ID книги
    title: str  # Поле для названия книги
    author: str  # Поле для автора книги
    year_of_publication: int = None  # Поле для года публикации, по умолчанию None
    isbn: str = None  # Поле для ISBN, по умолчанию None
    copies: int  # Поле для количества копий книги

    class Config:  # Конфигурация для модели
        from_attribute = True


# Схема для обновления книги в бд
class BookUpdate(BaseModel):
    title: str
    author: str
    year_of_publication: int
    isbn: str
    copies: int


# Схема для представления читателя в ответах API
class Reader(BaseModel):
    id: int  # Поле ID пользователя
    email: EmailStr  # Поле для email пользователя

    class Config:  # Конфигурация для модели
        from_attribute = True  # Включаем режим работы с ORM, чтобы Pydantic мог обрабатывать ORM-модели


# Схема для создания читателя
class ReaderCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr


# Схема для получения всех читателей
class ReaderGet(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str
    email: EmailStr


# Схема для обновления читателя
class ReaderUpdate(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr


# Схема для записи какой пользователь взял какую книгу
class BorrowBookRequest(BaseModel):
    book_title: str
    reader_email: str
    borrow_date: str
    return_date: str
