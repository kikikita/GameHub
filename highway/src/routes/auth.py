"""Authentication helpers for Telegram WebApp."""

from fastapi import APIRouter, Depends, Response

import json

from src.auth.tg_auth import verify_tg_data

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/session")
async def create_session(
    response: Response,
    user_data: dict = Depends(verify_tg_data),
) -> dict:
    """Authenticate user and set a secure cookie."""

    user_info = json.loads(user_data.get("user", "{}"))
    user_id = user_info.get("id")

    if not user_id:
        return {"status": "error", "message": "User not found in initData"}

    response.set_cookie(
        key="session_id",
        value=str(user_id),
        httponly=True,
        max_age=3600,
        secure=True,
        samesite="strict",
        path="/api",
    )
    return {"status": "ok"}
