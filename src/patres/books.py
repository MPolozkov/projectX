import os
from typing import List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Header

from jose import jwt
from sqlalchemy.orm import Session
from patres import crud, schemas
from patres.database import get_db

router = APIRouter()


@router.post("/books/", response_model=schemas.Book)
def create_book(
        book: schemas.BookCreate, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для создания новой книги"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")
    db_book = crud.create_book(db=db, book=book)
    return db_book


#
@router.get("/books/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для получения списка книг"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    books = crud.get_books(db=db)
    return books


@router.get("/book/{book_title}", response_model=schemas.BookUpdate)
def read_books_one(book_title: str, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для получения одной книги по email"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book_one = crud.get_book_by_title(db, book_title=book_title)
    if not db_book_one:
        raise HTTPException(status_code=404, detail="Reader not found")
    return db_book_one


@router.put("/books/{book_title}")
def update_book(
        book_title: str, book: schemas.BookUpdate, db: Session = Depends(get_db), token: Optional[str] = Header(None)
):
    """Эндпоинт для обновления книги"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book = crud.get_book_by_title(db, book_title=book_title)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for field, value in book.dict(exclude_defaults=True).items():
        setattr(db_book, field, value)

    update_books = crud.get_book_by_bd(db=db, db_book=db_book)
    return update_books


@router.delete("/books/{book_title}")
def delete_book(book_title: str, db: Session = Depends(get_db), token: str = Header(None)):
    """Эндпоинт для удаления книги"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")

    db_book = crud.get_book_by_title(db, book_title=book_title)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    return {f"Book {book_title} delete successfully"}
