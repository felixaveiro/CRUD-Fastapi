from db import Base
from sqlalchemy import Integer, Column, String, Boolean


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    author = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password = Column(
        String,
        nullable=False
    )
    is_active = Column(
        Boolean,
        default=True
    )