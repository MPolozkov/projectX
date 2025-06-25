from fastapi import APIRouter, Depends, HTTPException, Response  # Импортируем необходимые модули FastAPI
from sqlalchemy.orm import Session  # Импортируем сессии для работы с БД

from patres import schemas, security, crud
from patres.database import get_db


router = APIRouter()  # Создаем новый экземпляр маршрутизатора


# Эндпоинт для регистрации нового библиотекаря
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Получаем данные пользователя и сессию"""
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    hashed_password = security.get_password_hash(user.password)  # Хэшируем пароль пользователя
    user_data = schemas.UserCreate(email=user.email, password=hashed_password)
    # Создаем пользователя в базе данных.
    user_db = crud.create_user(db=db, user=user_data, )
    return user_db


# Эндпоинт для аутентификации библиотекаря
@router.post("/login")
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Получаем данные формы и сессию"""
    user = crud.get_user_by_email_login(db=db, email=form_data.email)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Такого пользователя не существует пройдите регистрацию")
    access_token = security.create_access_token(data={"sub": user.email})
    token = {"access_token": access_token, "token_type": "bearer"}
    return token
