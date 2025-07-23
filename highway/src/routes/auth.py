from fastapi import APIRouter, Depends, Response
from src.auth.tg_auth import verify_tg_data
import json

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/session")
async def create_session(response: Response, user_data: dict = Depends(verify_tg_data)):
    """
    Authenticates the user with their Telegram initData and sets a session cookie.
    The frontend should call this endpoint once when the app loads.
    """
    # The user_data is already validated by the verify_tg_data dependency.
    # We can use the user's ID as the session value.
    user_info = json.loads(user_data.get("user", "{}"))
    user_id = user_info.get("id")

    if not user_id:
        return {"status": "error", "message": "User not found in initData"}

    # Set a secure, HttpOnly cookie to maintain the session.
    # The browser will automatically send this cookie on subsequent requests.
    response.set_cookie(
        key="session_id",
        value=str(user_id),
        httponly=True,
        max_age=3600,
        secure=True,          # Only send over HTTPS
        samesite="strict",      # Required for cross-site contexts like iframes
        path="/api",
    )
    return {"status": "ok"} 