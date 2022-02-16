from xpresso import HTTPException, status

from app.models.schemas.auth import Unauthorized
from app.models.schemas.jwt import Token

PREFIX = "Token "
PREFIX_LENGTH = len(PREFIX)


def extract_token_from_authroization_header(authorization_header: str) -> Token:
    if not authorization_header.startswith(PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(
                reason="Invalid scheme in Authorization header"
            ),
        )
    return Token(authorization_header[PREFIX_LENGTH:])
