"""Endpoints for subscription management and plans."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.subscription import Subscription
from src.api.utils import resolve_user_id

router = APIRouter(prefix="/api/v1", tags=["payments"])


@router.get("/plans")
async def plans() -> list[dict[str, int | str]]:
    """List available subscription plans."""

    return [
        {"id": "free", "price": 0},
        {"id": "pro", "price": 299},
    ]


@router.post("/subscribe")
async def subscribe(
    plan: str = "pro",
    user_data: dict = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Initiate a subscription purchase."""

    user_id = await resolve_user_id(db, user_data)
    sub = Subscription(user_id=user_id, plan=plan, status="pending")
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return {
        "id": str(sub.id),
        "status": sub.status,
        "link": "https://pay.example.com/123",
    }


@router.get("/subscription/status")
async def subscription_status(
    user_data: dict = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Return the latest subscription status for the current user."""

    user_id = await resolve_user_id(db, user_data)
    res = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.started_at.desc())
    )
    sub = res.scalars().first()
    if not sub:
        return {"status": "canceled"}
    return {"status": sub.status}
