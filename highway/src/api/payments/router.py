"""Endpoints for subscription management and plans."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from pydantic import BaseModel

from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.subscription import Subscription
from src.api.utils import resolve_user_id, ensure_admin
from src.utils.tg_invoice import export_tg_invoice
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["payments"])


class Plan(BaseModel):
    id: str
    title: str
    price: float
    currency: str
    stars: int
    period: str
    wishes: int
    is_promo: bool = False
    old_price: float | None = None


@router.get("/plans/")
async def plans() -> list[Plan]:
    """List available subscription plans."""

    return [
        Plan(
            id="pro_3days",
            title="3 Days",
            price=0.01,
            currency="USD",
            stars=1,
            period="3 days",
            wishes=1,
            is_promo=True,
            old_price=0.99,
        ),
        Plan(
            id="pro_month",
            title="1 Month",
            price=5.99,
            currency="USD",
            stars=460,
            period="month",
            wishes=8,
        ),
        Plan(
            id="pro_quarter",
            title="3 Months",
            price=13.50,
            currency="USD",
            stars=1000,
            period="3 months",
            wishes=21,
        ),
        Plan(
            id="pro_year",
            title="1 Year",
            price=40.99,
            currency="USD",
            stars=3150,
            period="year",
            wishes=70,
        ),
    ]


@router.post("/subscribe/")
async def subscribe(
    plan: str = "pro",
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Initiate a subscription purchase."""
    user_id = await resolve_user_id(tg_id, db)
    logger.info(f"Initiating subscription purchase for tg user {tg_id}")
    plans_list = await plans()
    plan_data = next((p for p in plans_list if p.id == plan), None)
    if plan_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan",
        )
    link, payload = export_tg_invoice(
        item_title=f"PRO plan ({plan_data.title})",
        item_id=plan,
        amount_stars=plan_data.stars,
        item_description=f"PRO plan ({plan_data.title})",
    )

    sub = Subscription(
        user_id=user_id, plan=plan, status="pending", invoice_payload=payload
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    logger.info(f"Created invoice {payload} for user {user_id}")
    return {
        "id": str(sub.id),
        "status": sub.status,
        "link": link,
    }


class InvoicePayload(BaseModel):
    invoice_payload: str


@router.post("/subscription/verify/")
async def verify_subscription_payload(
    payload: InvoicePayload, db: AsyncSession = Depends(get_session)
) -> dict:
    """Verify the subscription payload."""
    logger.info(f"Verifying subscription payload {payload.invoice_payload}")    
    res = await db.execute(
        select(Subscription).where(
            Subscription.invoice_payload == payload.invoice_payload,
            Subscription.status == "pending",
        )
    )
    sub = res.scalars().first()
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    logger.info(f"Subscription payload {payload.invoice_payload} verified!")
    return {"status": "success"}


@router.post("/subscription/confirm/")
async def confirm_subscription(
    payload: InvoicePayload, db: AsyncSession = Depends(get_session)
) -> dict:
    """Confirm the subscription."""
    logger.info(f"Confirming subscription for payload {payload.invoice_payload}")
    res = await db.execute(
        select(Subscription).where(
            Subscription.invoice_payload == payload.invoice_payload,
            Subscription.status == "pending",
        )
    )
    sub = res.scalars().first()
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )

    # Top up user wishes according to the purchased plan
    plans_list = await plans()
    plan_data = next((p for p in plans_list if p.id == sub.plan), None)
    user = await db.get(User, sub.user_id)
    if user and plan_data:
        user.wishes += plan_data.wishes

    sub.status = "active"
    await db.commit()
    await db.refresh(sub)
    logger.info(f"Successfully confirmed subscription for user {sub.user_id}!")
    return {"status": "success"}


@router.get("/subscription/")
async def get_subscription(
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Return the current subscription plan for the user."""
    user_id = await resolve_user_id(tg_id, db)
    res = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        )
    )
    sub = res.scalars().first()
    if not sub:
        return {"plan": "free"}
    return {"plan": "pro"}


@router.post("/subscription/change-plan/")
async def change_plan(
    plan: str,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Force change of the user's subscription plan."""
    user_id = await resolve_user_id(tg_id, db)
    ensure_admin(tg_id)
    if plan not in {"pro"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan",
        )

    sub = Subscription(user_id=user_id, plan=plan, status="active")
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return {"id": str(sub.id), "plan": sub.plan, "status": sub.status}