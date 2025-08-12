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

async def has_pro_plan(db: AsyncSession, user_id: int) -> bool:
    """Check if the user has an active Pro subscription."""
    res = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.started_at.desc())
    )
    sub = res.scalars().first()
    return sub and sub.plan == "pro" and sub.status == "active"


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


def get_localized(value, lang: str):
    """Return localized value from a dict based on the language.

    If ``value`` is a mapping of languages (``{"ru": "...", "en": "..."}``),
    choose the text for ``lang``. If not available, fall back to ``ru`` or the
    first available entry. For nested structures lists/dicts are processed
    recursively.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        if all(isinstance(v, str) for v in value.values()):
            return value.get(lang) or value.get("ru") or next(iter(value.values()), None)
        return {k: get_localized(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [get_localized(v, lang) for v in value]
    return value
