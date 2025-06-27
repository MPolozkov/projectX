import os
from typing import List, Set

# from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from patres import crud, schemas, models, security
from sqlalchemy.orm import Session
from patres.database import get_db
from typing import Optional, Dict, List
from jose import jwt

# Создаем новый экземпляр маршрутизатора
router = APIRouter()


@router.post("/borrowed_book/{book_title}/{reader_email}")
async def borrow_book(book_title: str,
                      reader_email: str,
                      db: Session = Depends(get_db),
                      token: Optional[str] = Header(None)):

    """Эндпоинт выдачи книги"""
    security.decode_access_token(db=db, token=token)
    bor_book = crud.borrowed_book(db, book_title=book_title, reader_email=reader_email)
    return bor_book


@router.post("/return_book/{book_title}/{reader_email}")
async def return_book(book_title: str,
                      reader_email: str,
                      db: Session = Depends(get_db),
                      token: str = Header(None)):

    """Эндпоинт для возврата книг"""
    security.decode_access_token(db=db, token=token)
    book = crud.return_book(db, book_title=book_title, reader_email=reader_email)
    return book
