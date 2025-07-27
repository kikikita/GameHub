"""Utility helpers for API handlers."""

import json
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User


async def resolve_user_id(db: AsyncSession, user_data: dict) -> int:
    """Return internal user id using telegram data."""
    tg_id = None
    if user_data.get("user_id") is not None:
        tg_id = user_data["user_id"]
    elif user_data.get("id") is not None:
        tg_id = user_data["id"]
    else:
        raw = user_data.get("user")
        if isinstance(raw, str):
            try:
                tg_id = json.loads(raw).get("id")
            except Exception:
                tg_id = None
    if tg_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data",
        )
    result = await db.execute(select(User).where(User.tg_id == int(tg_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user.id
