from pydantic import BaseModel


# -----------------------------
# Book Schemas
# -----------------------------
class BookBase(BaseModel):
    title: str
    author: str
    description: str
    year: int


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        from_attributes = True


# -----------------------------
# Authentication Schemas
# -----------------------------
class CreateUserRequest(BaseModel):
    username: str
    password: str


class UpdateProfileRequest(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True