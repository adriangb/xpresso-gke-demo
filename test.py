import json
from typing import AbstractSet, ClassVar, Generic, Literal, Type, TypeVar

from pydantic import BaseModel
from xpresso import FromHeader


class XpressoSecurityScheme:
    type: ClassVar[Literal["oauth2", "http"]]
    scheme_name: ClassVar[str]


class OAuth2Base(XpressoSecurityScheme):
    type: ClassVar[Literal["oauth2"]] = "oauth2"
    scopes: ClassVar[AbstractSet[str]]
    token: str

    def __init__(self, token: str) -> None:
        self.token = token


class OAuth2(OAuth2Base):
    @classmethod
    def extract(cls, token: FromHeader[str]) -> "OAuth2":
        return cls(token=token)


class SecurityModel(BaseModel):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        # verify that all fields are either SecurityModel types or XpressoSecurityScheme types


class UserOAuth2Model(OAuth2):
    scheme_name = "oauth2"
    scopes = {"scope1", "scope2"}


UserModelType = TypeVar("UserModelType", bound=BaseModel)


class EnforcedOAuth2Model(OAuth2Base, Generic[UserModelType]):
    user_model: ClassVar[Type[UserModelType]]  # type: ignore[misc]
    user: UserModelType

    def __init__(self, user: UserModelType, token: str) -> None:
        super().__init__(token)
        self.user = user

    @classmethod
    async def extract(
        cls, token: FromHeader[str]
    ) -> "EnforcedOAuth2Model[UserModelType]":
        payload = json.loads(token)  # or validate JWT, etc.
        scopes = set(payload["scopes"])
        assert scopes.issuperset(cls.scopes)
        return cls(user=cls.user_model(**payload), token=token)


class MyUserModel(BaseModel):
    name: str


class UserEnforcedOAuth2Model(EnforcedOAuth2Model[MyUserModel]):
    user_model = MyUserModel
