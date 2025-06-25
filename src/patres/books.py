import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header

from jose import jwt
from sqlalchemy.orm import Session
from patres import crud, schemas, security
from patres.database import get_db

router = APIRouter()


@router.post("/books/", response_model=schemas.Book)
def create_book(
        book: schemas.BookCreate, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для создания новой книги"""
    security.decode_access_token(db=db, token=token)
    db_book = crud.create_book(db=db, book=book)
    return db_book


#
@router.get("/books/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для получения списка книг"""
    security.decode_access_token(db=db, token=token)
    books = crud.get_books(db=db)
    return books


@router.get("/book/{book_title}", response_model=schemas.BookUpdate)
def read_books_one(book_title: str, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для получения одной книги по названию"""
    security.decode_access_token(db=db, token=token)
    db_book_one = crud.get_book_by_title(db, book_title=book_title)
    return db_book_one


@router.put("/books/{book_title}")
def update_book(
        book_title: str, book: schemas.BookUpdate, db: Session = Depends(get_db), token: Optional[str] = Header(None)
):
    """Эндпоинт для обновления книги"""
    security.decode_access_token(db=db, token=token)

    db_book = crud.get_book_by_title(db, book_title=book_title)

    for field, value in book.dict(exclude_defaults=True).items():
        setattr(db_book, field, value)

    update_books = crud.get_book_by_bd(db=db, db_book=db_book)
    return update_books


@router.delete("/delete/{book_title}")
def delete_book(book_title: str, db: Session = Depends(get_db), token: str = Header(None)):
    """Эндпоинт для удаления книги"""
    security.decode_access_token(db=db, token=token)
    db_book = crud.get_book_by_title_delete(db, book_title=book_title)
    return db_book
