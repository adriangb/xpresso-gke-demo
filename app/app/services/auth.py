from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from pydantic import ValidationError
from xpresso.dependencies.models import Singleton

from app.config import AuthConfig
from app.models.schemas.jwt import JWTUser, Token

ALGORITHM = "HS256"
ALGORITHMS = [ALGORITHM]


class InvalidTokenError(Exception):
    pass


class Now(Protocol):
    def __call__(self) -> datetime:
        ...


@dataclass(slots=True)
class AuthService(Singleton):
    config: AuthConfig
    expiration_timedelta: timedelta = timedelta(weeks=1)
    now: Now = datetime.utcnow
    hasher: PasswordHasher = PasswordHasher()

    @property
    def secret_key(self) -> str:
        return self.config.token_signing_key.get_secret_value()

    def create_access_token(self, user_id: UUID) -> Token:
        exp = (self.now() + self.expiration_timedelta).timestamp()
        jwt_user = JWTUser.construct(exp=exp, sub=str(user_id))
        jwt_payload = jwt_user.dict(by_alias=True)
        return jwt.encode(jwt_payload, self.secret_key, algorithm=ALGORITHM)  # type: ignore[misc,return-value]

    def verify_access_token_and_extract_user_id(self, token: Token) -> UUID:
        try:
            user_id = JWTUser(
                **jwt.decode(  # type: ignore  # for Pylance
                    token, self.secret_key, algorithms=ALGORITHMS
                )
            ).user_id
            return UUID(user_id)
        except jwt.PyJWTError as decode_error:
            raise InvalidTokenError("Unable to decode JWT token") from decode_error
        except ValidationError as validation_error:
            raise InvalidTokenError("Malformed payload in token") from validation_error
