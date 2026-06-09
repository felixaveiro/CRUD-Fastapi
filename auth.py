from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from db import SessionLocal
from models import Users


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

SECRET_KEY = "cc708c1e565a3e4adfa4d694154ec8eee3cd6ddc9faf55327a37cd2870612ccc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token"
)


# -----------------------------
# Schemas
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


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# -----------------------------
# Authentication Helpers
# -----------------------------
def authenticate_user(
    username: str,
    password: str,
    db: Session
):
    user = (
        db.query(Users)
        .filter(Users.username == username)
        .first()
    )

    if not user:
        return False

    if not bcrypt_context.verify(
        password,
        user.hashed_password
    ):
        return False

    return user


def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta
):
    payload = {
        "sub": username,
        "id": user_id
    }

    expire = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)]
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )

        return {
            "id": user_id,
            "username": username
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )


# -----------------------------
# Register
# -----------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    create_user_request: CreateUserRequest,
    db: db_dependency
):
    existing_user = (
        db.query(Users)
        .filter(
            Users.username ==
            create_user_request.username
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(
            create_user_request.password
        )
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {
        "message": "User created successfully"
    }


# -----------------------------
# Login
# -----------------------------
@router.post(
    "/token",
    response_model=Token
)
async def login_for_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: db_dependency
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    token = create_access_token(
        user.username,
        user.id,
        timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------------
# Get Current User Profile
# -----------------------------
@router.get(
    "/me",
    response_model=UserProfile
)
async def get_me(
    current_user: Annotated[
        dict,
        Depends(get_current_user)
    ],
    db: db_dependency
):
    user = (
        db.query(Users)
        .filter(
            Users.id == current_user["id"]
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# -----------------------------
# Update Profile
# -----------------------------
@router.put(
    "/me",
    response_model=UserProfile
)
async def update_me(
    profile: UpdateProfileRequest,
    current_user: Annotated[
        dict,
        Depends(get_current_user)
    ],
    db: db_dependency
):
    user = (
        db.query(Users)
        .filter(
            Users.id == current_user["id"]
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.username = profile.username

    db.commit()
    db.refresh(user)

    return user