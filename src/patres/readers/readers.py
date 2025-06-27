from typing import Optional

from fastapi import APIRouter, Depends, Header

from sqlalchemy.orm import Session
from patres import crud, schemas, security
from patres.database import get_db


router = APIRouter()


@router.post("/readers/", response_model=schemas.Reader)
def create_reader(reader: schemas.ReaderCreate, db: Session = Depends(get_db)):
    """Эндпоинт для регистрации читателя с проверкой есть такой читатель или нет"""
    crud.get_reader_by_email(db=db, email=reader.email)
    reader_db = crud.create_readers(db=db, reader=reader)
    return reader_db


@router.get("/reader/{reader_email}", response_model=schemas.ReaderUpdate)
def read_reader(reader_email: str, db: Session = Depends(get_db)):
    """Эндпоинт для получения одного читателя по email"""
    db_reader = crud.get_reader_by_one(db, reader_email=reader_email)
    return db_reader


@router.get("/readers/", response_model=list[schemas.ReaderGet])
def list_readers(db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для получения всех читателей"""
    security.decode_access_token(db=db, token=token)
    readers_get = crud.get_reader(db=db)
    return readers_get


@router.put("/readers/{reader_email}")
def update_reader(
    reader_email: str, reader: schemas.ReaderUpdate, db: Session = Depends(get_db), token: Optional[str] = Header(None)
):
    """Эндпоинт для редактирования читателя"""
    security.decode_access_token(db=db, token=token)
    reader_up = crud.get_reader_by_bd(db=db, reader_email=reader_email, reader_update=reader)
    return reader_up


@router.delete("/readers/{reader_email}")
def delete_reader(reader_email: str, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Эндпоинт для удаления читателя из бд"""
    security.decode_access_token(db=db, token=token)

    db_readers = crud.readers_delete(db, reader_email=reader_email)
    return db_readers
