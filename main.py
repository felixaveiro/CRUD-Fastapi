from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import services
import models
import schemas
import auth

from db import get_db, create_table

app = FastAPI(
    title="Bookstore API"
)

app.include_router(auth.router)

create_table()


@app.get("/")
def root():
    return {
        "message": "Bookstore API is running"
    }


@app.get("/books/", response_model=list[schemas.Book])
def get_all_books(db: Session = Depends(get_db)):
    return services.get_books(db)


@app.get("/books/{id}", response_model=schemas.Book)
def get_book_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    book_queryset = services.get_book(db, id)

    if not book_queryset:
        raise HTTPException(
            status_code=404,
            detail="Invalid book id provided"
        )

    return book_queryset


@app.post("/books/", response_model=schemas.Book)
def create_new_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db)
):
    return services.create_book(db, book)


@app.put("/books/{id}", response_model=schemas.Book)
def update_book(
    id: int,
    book: schemas.BookCreate,
    db: Session = Depends(get_db)
):
    db_update = services.update_book(
        db,
        book,
        id
    )

    if not db_update:
        raise HTTPException(
            status_code=404,
            detail="Book is not found"
        )

    return db_update


@app.delete("/books/{id}", response_model=schemas.Book)
def delete_book(
    id: int,
    db: Session = Depends(get_db)
):
    delete_entry = services.delete_book(
        db,
        id
    )

    if not delete_entry:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return delete_entry