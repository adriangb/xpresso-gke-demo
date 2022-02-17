from pydantic import BaseModel, EmailStr, HttpUrl

from app.models.schemas.configs import ModelInRequestConfig, ModelInResponseConfig


class User(BaseModel):
    username: str
    email: str
    bio: str | None = None
    image: str | None = None


class UserForLogin(BaseModel):
    email: EmailStr
    password: str

    Config = ModelInRequestConfig


class UserInLogin(BaseModel):
    user: UserForLogin

    Config = ModelInRequestConfig


class UserForCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    Config = ModelInRequestConfig


class UserInCreate(BaseModel):
    user: UserForCreate

    Config = ModelInRequestConfig


class UserForUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    bio: str | None = None
    image: HttpUrl | None = None

    Config = ModelInRequestConfig


class UserInUpdate(BaseModel):
    user: UserForUpdate

    Config = ModelInRequestConfig


class UserWithToken(User):
    token: str

    Config = ModelInResponseConfig


class UserInResponse(BaseModel):
    user: UserWithToken

    Config = ModelInResponseConfig
