from fastapi import Request, HTTPException, Header
import logging
from settings import settings

logger = logging.getLogger(__name__)

def auth_server(
    request: Request,
    x_server_auth: str | None = Header(default=None)
) -> int:
    if not x_server_auth:
        logger.error(f"Request to {request.url.path} rejected: Authentication is missing")
        raise HTTPException(status_code=401, detail="Authentication is missing")
    
    token = x_server_auth
    
    if token != settings.bots.server_auth_token.get_secret_value():
        logger.error(f"Request to {request.url.path} rejected: Invalid server auth token")
        raise HTTPException(status_code=403, detail="Invalid server auth token")
    
    return True