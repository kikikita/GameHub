"""Utility helpers for API handlers."""

import json
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.models.subscription import Subscription
from src.config import settings


async def ensure_pro_plan(db: AsyncSession, user_id: int) -> None:
    """Raise 403 if the user doesn't have an active Pro subscription."""

    res = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.started_at.desc())
    )
    sub = res.scalars().first()
    if not sub or sub.plan != "pro" or sub.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Feature available only on the Pro plan",
        )


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


def ensure_admin(user_data: dict) -> None:
    """Raise 403 if the requester is not an admin."""
    tg_id = None
    if user_data.get("user_id") is not None:
        tg_id = int(user_data["user_id"])
    elif user_data.get("id") is not None:
        tg_id = int(user_data["id"])
    else:
        raw = user_data.get("user")
        if isinstance(raw, str):
            try:
                tg_id = int(json.loads(raw).get("id"))
            except Exception:
                tg_id = None
    if tg_id is None or tg_id not in settings.admin_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
