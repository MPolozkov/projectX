import os
from typing import List, Set

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from patres import crud, schemas, models, security
from sqlalchemy.orm import Session
from patres.database import get_db
from typing import Optional, Dict, List
from jose import jwt

# Создаем новый экземпляр маршрутизатора
router = APIRouter()


@router.post("/borrowed_book/")
async def borrow_book(book_title: str,
                      reader_email: str,
                      db: Session = Depends(get_db),
                      token: Optional[str] = Header(None)):

    """Эндпоинт выдачи книги"""
    security.decode_access_token(db=db, token=token)

    try:
        book = db.query(models.Book).filter(models.Book.title == book_title, models.Book.copies > 0).first()

        # Проверка, найдена ли книга
        if not book:
            raise HTTPException(status_code=404, detail="Книга не найдена или все экземпляры выданы.")

        # Бизнес логика 1: Проверка наличия экземпляров
        if book.copies == 0:
            raise HTTPException(status_code=400, detail="Доступных экземпляров этой книги нет")

        # Бизнес логика 2: Проверка лимита книг у читателя
        borrowed_books = (
            db.query(models.BorrowedBook)
            .filter(models.BorrowedBook.reader_email == reader_email, models.BorrowedBook.return_date.is_(None))
            .count()
        )
        if borrowed_books >= 3:
            raise HTTPException(status_code=400, detail="У вас достигнут лимит книг")

        # Выдача книги
        book.copies -= 1
        new_borrow = models.BorrowedBook(
            reader_email=reader_email, book_title=book_title, borrow_date=datetime.now(), return_date=None
        )
        db.add(new_borrow)
        db.commit()
        db.refresh(book)

        return {"Book borrowed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/return_book")
async def return_book(book_title: str,
                      reader_email: str,
                      db: Session = Depends(get_db),
                      token: str = Header(None)):

    """Эндпоинт для возврата книг"""
    security.decode_access_token(db=db, token=token)

    try:
        # Находим запись о выданной книге, которую нужно вернуть
        borrowed_book = (
            db.query(models.BorrowedBook)
            .filter(
                models.BorrowedBook.reader_email == reader_email,
                models.BorrowedBook.book_title == book_title,
                models.BorrowedBook.return_date.is_(None),
            )
            .first()
        )

        # Проверяем, найдена ли запись о выдаче книги
        if not borrow_book:
            raise HTTPException(status_code=404, detail="Книга не найдена в спмске выданных или уже возвращена")

        # Отмечаем книгу как возвращенную
        borrowed_book.return_date = datetime.now()

        # Увеличиваем количество доступных экземпляров книги
        book = db.query(models.Book).filter(models.Book.title == book_title).first()
        if book:
            book.copies += 1
        else:
            raise HTTPException(status_code=404, detail="Книга не найдена в базе данных")

        # Фиксируем изменения в базе данных
        db.commit()

        return {"Книга возвращена успешно"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
