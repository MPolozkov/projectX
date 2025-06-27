from fastapi import APIRouter, Depends, HTTPException, Response  # Импортируем необходимые модули FastAPI
from sqlalchemy.orm import Session  # Импортируем сессии для работы с БД

from patres import schemas, security, crud
from patres.database import get_db


router = APIRouter()  # Создаем новый экземпляр маршрутизатора


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Эндпоинт для регистрации нового библиотекаря"""
    crud.get_user_by_email(db=db, email=user.email)
    hashed_password = security.get_password_hash(user.password)
    user_data = schemas.UserCreate(email=user.email, password=hashed_password)
    user_db = crud.create_user(db=db, user=user_data, )
    return user_db


@router.post("/login")
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Эндпоинт для аутентификации библиотекаря"""
    user = crud.get_user_by_email_login(db=db, email=form_data.email, password=form_data.password)
    access_token = security.create_access_token(data={"sub": user.email})
    token = {"access_token": access_token, "token_type": "bearer"}
    return token
