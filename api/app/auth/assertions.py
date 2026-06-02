import jwt

from app.auth.errors import InvalidTokenError, UnauthorizedDomainError
from app.auth.tokens import decode_token

AUTHORIZED_DOMAIN = "@unq.edu.ar"


def ensure_token_decoded(token: str, expected_type: str) -> dict:
    try:
        return decode_token(token, expected_type=expected_type)
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError() from e


def ensure_authorized_domain(email: str) -> None:
    if not email.endswith(AUTHORIZED_DOMAIN):
        raise UnauthorizedDomainError(AUTHORIZED_DOMAIN)
