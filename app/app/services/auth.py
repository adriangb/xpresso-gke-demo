from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

import jwt
from pydantic import ValidationError
from xpresso.encoders.api import Encoder
from xpresso.encoders.json import JsonableEncoder

from app.models.schemas.jwt import JWTUser, Token

ALGORITHM = "HS256"
ALGORITHMS = [ALGORITHM]


class InvalidTokenError(Exception):
    pass


class Now(Protocol):
    def __call__(self) -> datetime:
        ...


@dataclass(frozen=True, slots=True, eq=False)
class AuthService:
    secret_key: str
    expiration_timedelta: timedelta = timedelta(weeks=1)
    now: Now = datetime.utcnow
    encoder: Encoder = JsonableEncoder(custom_encoder={datetime: datetime.timestamp})

    def create_access_token(self, user_id: UUID) -> Token:
        jwt_user = JWTUser.construct(
            exp=self.now() + self.expiration_timedelta, user_id=user_id
        )
        jwt_payload = self.encoder(jwt_user.dict(by_alias=True))
        return jwt.encode(jwt_payload, self.secret_key, algorithm=ALGORITHM)  # type: ignore[misc,return-value]

    def verify_access_token_and_extract_user_id(self, token: Token) -> UUID:
        try:
            return JWTUser(
                **jwt.decode(  # type: ignore  # for Pylance
                    token, self.secret_key, algorithms=ALGORITHMS
                )
            ).user_id
        except jwt.PyJWTError as decode_error:
            raise InvalidTokenError("Unable to decode JWT token") from decode_error
        except ValidationError as validation_error:
            raise InvalidTokenError("Malformed payload in token") from validation_error
