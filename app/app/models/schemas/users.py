from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl

from app.models.domain.users import User


class UserInLoginInfo(BaseModel):
    email: EmailStr
    password: str


class UserInLogin(BaseModel):
    user: UserInLoginInfo


class UserCreateInfo(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInCreate(BaseModel):
    user: UserCreateInfo


class UserUpdateInfo(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None


class UserInUpdate(BaseModel):
    user: UserUpdateInfo


class UserWithToken(User):
    token: str


class UserInResponse(BaseModel):
    user: UserWithToken
