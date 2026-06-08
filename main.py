from fastapi import FastAPI, Depends, HTTPException
import services, models, schemas
from db import get_db, engine, create_table   # ← fixed
from sqlalchemy.orm import Session
import auth

app = FastAPI()
app.include_router(auth.router)
create_table()

@app.get("/books/", response_model=list[schemas.Book])
def get_all_books(db: Session = Depends(get_db)):
    return services.get_books(db)

@app.get("/book/{id}", response_model=schemas.Book)
def get_book_by_id(id: int, db: Session = Depends(get_db)):
    book_queryset = services.get_book(db, id)
    if book_queryset:
        return book_queryset
    raise HTTPException(status_code=404, detail="Invalid book id provided")

@app.post("/books/", response_model=schemas.Book)
def create_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return services.create_book(db, book)

@app.put("/book/{id}", response_model=schemas.Book)
def update_book(book: schemas.BookCreate, id: int, db: Session = Depends(get_db)):
    db_update = services.update_book(db, book, id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Book is not found")
    return db_update

@app.delete("/books/{id}", response_model=schemas.Book)
def delete_book(id: int, db: Session = Depends(get_db)):
    delete_entry = services.delete_book(db, id)
    if not delete_entry:
        raise HTTPException(status_code=404, detail="Book not found")
    return delete_entry