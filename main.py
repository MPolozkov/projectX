from fastapi import FastAPI
from src.patres import auth, books
from src.patres.readers import readers
from src.patres.borrowed_book import borrowed_book

app = FastAPI()  # Создание экземпляра FastAPI приложения

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(readers.router)
app.include_router(borrowed_book.router)


@app.get("/")
async def root():
    return {"/"}
