import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import HTTPException, Header, Request
import logging
from src.config import settings

logger = logging.getLogger(__name__)


def authenticate_server(
    request: Request,
    x_server_auth: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> int:
    if x_server_auth and x_user_id:
        return auth_server(request, x_server_auth, x_user_id)
    return None


def authenticated_user(
    request: Request,
    authorization: str | None = Header(default=None),
    x_server_auth: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> int:
    if x_server_auth and x_user_id:
        return auth_server(request, x_server_auth, x_user_id)

    if not authorization:
        logger.error(
            f"Request to {request.url.path} rejected: Authentication is missing"
        )
        raise HTTPException(status_code=401, detail="Authentication is missing")

    return auth_tg(request, authorization)


def _is_valid_tg_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    Validate initData from a Telegram Web App.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    On success, returns the parsed data dictionary.
    On failure, returns None.
    """
    try:
        # The data is in query string format
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        logger.warning("Could not parse initData: %s", init_data)
        return None

    if "hash" not in parsed_data:
        logger.warning("Hash not in initData: %s", parsed_data)
        return None

    init_data_hash = parsed_data.pop("hash")

    # The data-check-string is a concatenation of all received fields,
    # sorted alphabetically, in the format key=<value> with a line feed character ('\n', 0x0A) used as separator.
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items()) if k != "hash"
    )

    # The secret key is the HMAC-SHA-256 hash of the bot token with "WebAppData" as data.
    secret_key = hmac.new(
        "WebAppData".encode(), bot_token.encode(), hashlib.sha256
    ).digest()

    # The calculated hash is the HMAC-SHA-256 hash of the data-check-string with the secret key.
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if calculated_hash == init_data_hash:
        return parsed_data

    logger.warning("Hash mismatch on validation")
    return None


def auth_tg(request: Request, authorization: str | None = Header(default=None)) -> int:
    if authorization.lower().startswith("tma "):
        init_data = authorization[4:]
    else:
        init_data = authorization

    validated_data = _is_valid_tg_init_data(
        init_data, settings.tg_bot_token.get_secret_value()
    )

    if validated_data is None:
        logger.error(
            f"Request to {request.url.path} rejected: Invalid initData in header"
        )
        raise HTTPException(status_code=403, detail="Invalid initData")

    return json.loads(validated_data.get("user", "{}")).get("id")


def auth_server(request: Request, x_server_auth: str, x_user_id: str) -> int:
    if not x_server_auth:
        logger.error(
            f"Request to {request.url.path} rejected: Authentication is missing"
        )
        raise HTTPException(status_code=401, detail="Authentication is missing")

    token = x_server_auth

    if token != settings.server_auth_token.get_secret_value():
        logger.error(
            f"Request to {request.url.path} rejected: Invalid server auth token"
        )
        raise HTTPException(status_code=403, detail="Invalid server auth token")

    return int(x_user_id)


def verify_tg_data(
    request: Request, authorization: str | None = Header(default=None)
) -> dict:
    """
    FastAPI dependency to verify Telegram initData.
    Expects initData in the "Authorization" header, e.g., "tma <initData>".
    """
    if not authorization:
        logger.error(
            f"Request to {request.url.path} rejected: Authorization header is missing"
        )
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    # Support "tma <initData>" or just "<initData>"
    if authorization.lower().startswith("tma "):
        init_data = authorization[4:]
    else:
        init_data = authorization

    validated_data = _is_valid_tg_init_data(
        init_data, settings.tg_bot_token.get_secret_value()
    )

    if validated_data is None:
        logger.error(f"Request to {request.url.path} rejected: Invalid initData")
        raise HTTPException(status_code=403, detail="Invalid initData")

    return validated_data
