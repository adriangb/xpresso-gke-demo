from pydantic import BaseModel, EmailStr, HttpUrl

from app.models.domain.users import User as UserDomainModel


class User(BaseModel):
    username: str
    email: str
    bio: str | None = None
    image: str | None = None


class UserForLogin(BaseModel):
    email: EmailStr
    password: str


class UserInLogin(BaseModel):
    user: UserForLogin


class UserForCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInCreate(BaseModel):
    user: UserForCreate


class UserForUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    bio: str | None = None
    image: HttpUrl | None = None


class UserInUpdate(BaseModel):
    user: UserForUpdate


class UserWithToken(User):
    token: str

    @staticmethod
    def from_domain_model(user: UserDomainModel, token: str) -> "UserWithToken":
        return UserWithToken(
            username=user.username,
            email=user.email,
            bio=user.bio,
            image=user.image,
            token=token,
        )


class UserInResponse(BaseModel):
    user: UserWithToken
