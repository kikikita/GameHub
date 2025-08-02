"""Utility helpers for API handlers."""

import os
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.subscription import Subscription
from src.config import settings
from src.models.user import User


async def resolve_user_id(tg_id: int | None, db: AsyncSession) -> int:
    """Resolve the user ID from the request."""
    result = await db.execute(select(User).where(User.tg_id == int(tg_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user.id


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


def ensure_admin(tg_id: int) -> None:
    """Raise 403 if the requester is not an admin."""

    admins = settings.admin_ids
    if not admins:
        raw = os.getenv("ADMIN_ID")
        if raw:
            admins = [int(x) for x in raw.split(",") if x]

    if tg_id not in admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
