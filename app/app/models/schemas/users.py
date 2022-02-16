from typing import Optional

from app.models.domain.users import User
from pydantic import BaseModel, EmailStr, HttpUrl


class UserInLogin(BaseModel):
    email: EmailStr
    password: str


class _UserInCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInCreate(BaseModel):
    user: _UserInCreate


class UserInUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None


class UserWithToken(User):
    token: str


class UserInResponse(BaseModel):
    user: UserWithToken
