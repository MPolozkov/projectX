from typing import List

from fastapi import APIRouter, Depends, HTTPException, Header

from jose import jwt
from sqlalchemy.orm import Session
from patres import crud, schemas
from patres.database import get_db
from patres.security import SECRET_KEY, ALGORITHM

router = APIRouter()


# Эндпоинт для создания новой книги
@router.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")
    db_book = crud.create_book(db=db, book=book)
    return db_book


# Эндпоинт для получения списка книг
@router.get("/books/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db), token: str = Header(None)):  # Получаем параметры для пагинации
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    books = crud.get_books(db=db)  # Получаем книги из БД
    return books  # Возвращаем список книг


# Эндпоинт для получения одной книги по email
@router.get("/book/{book_title}", response_model=schemas.BookUpdate)
def read_books_one(book_title: str, db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book_one = crud.get_book_by_title(db, book_title=book_title)
    if not db_book_one:
        raise HTTPException(status_code=404, detail="Reader not found")
    return db_book_one


# Эндпоинт для обновления книги
@router.put("/books/{book_title}")
def update_book(book_title: str, book: schemas.BookUpdate, db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book = crud.get_book_by_title(db, book_title=book_title)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Обновляем поля книги данными из запроса
    for field, value in book.dict(exclude_defaults=True).items():
        setattr(db_book, field, value)

    update_books = crud.get_book_by_bd(db=db, db_book=db_book)
    return update_books


# Эндпоинт для удаления книги
@router.delete("/books/{book_title}")
def delete_book(book_title: str, db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book = crud.get_book_by_title(db, book_title=book_title)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    return {"message": f"Book {book_title} delete successfully"}
