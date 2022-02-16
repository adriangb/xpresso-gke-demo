from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

import jwt
from app.models.schemas.jwt import JWTUser, Token
from pydantic import ValidationError

ALGORITHM = "HS256"
ALGORITHMS = [ALGORITHM]


class InvalidTokenError(Exception):
    pass


@dataclass
class AuthService:
    secret_key: str
    expiration_timedelta: timedelta = timedelta(weeks=1)

    def create_access_token(self, user_id: UUID) -> Token:
        jwt_user = JWTUser.construct(exp=datetime.utcnow(), user_id=user_id)
        jwt_payload = jwt_user.dict(by_alias=True)
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
