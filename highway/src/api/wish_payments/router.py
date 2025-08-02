from pydantic import BaseModel
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from sqlalchemy import select
from src.utils.tg_invoice import export_tg_invoice
from src.api.utils import resolve_user_id
from src.auth.tg_auth import authenticated_user
from src.models.bundle_purchase import BundlePurchase

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/v1/wishes", tags=["payments"])


class WishBundle(BaseModel):
    id: str
    title: str
    price: float
    currency: str
    stars: int
    wishes: int
    is_promo: bool = False
    image_url: str | None = None
    old_price: float | None = None


@router.get("/bundles/")
async def bundles() -> list[WishBundle]:
    """List available subscription plans."""

    return [
        WishBundle(
            id="wishes_1",
            title="20 wishes",
            price=0.01,
            currency="USD",
            stars=1,  # 383
            wishes=20,
            is_promo=True,
            old_price=4.99,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_xxxs.webp",
        ),
        WishBundle(
            id="wishes_2",
            title="50 wishes",
            price=10.99,
            currency="USD",
            stars=845,
            wishes=50,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_xm.webp",
        ),
        WishBundle(
            id="wishes_3",
            title="150 wishes",
            price=29.99,
            currency="USD",
            stars=2300,
            wishes=150,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_xss.webp",
        ),
        WishBundle(
            id="wishes_4",
            title="300 wishes",
            price=49.99,
            currency="USD",
            stars=3845,
            wishes=300,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_l.webp",
        ),
        WishBundle(
            id="wishes_5",
            title="500 wishes",
            price=75.99,
            currency="USD",
            stars=5845,
            wishes=500,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_xl.webp",
        ),
        WishBundle(
            id="wishes_6",
            title="1000 wishes",
            price=99.99,
            currency="USD",
            stars=7690,
            wishes=1000,
            image_url="https://storage.yandexcloud.net/immersia-static-images/wish-bundles/wishes_xxl.webp",
        ),
    ]


class InvoicePayload(BaseModel):
    invoice_payload: str


@router.post("/verify/")
async def verify_bundle_payload(
    payload: InvoicePayload, db: AsyncSession = Depends(get_session)
) -> dict:
    """Verify the subscription payload."""
    logger.info(f"Verifying subscription payload {payload.invoice_payload}")
    res = await db.execute(
        select(BundlePurchase).where(
            BundlePurchase.invoice_payload == payload.invoice_payload,
            BundlePurchase.status == "pending",
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


@router.post("/confirm/")
async def confirm_bundle(
    payload: InvoicePayload, db: AsyncSession = Depends(get_session)
) -> dict:
    """Confirm the bundle."""
    logger.info(f"Confirming bundle for payload {payload.invoice_payload}")
    res = await db.execute(
        select(BundlePurchase).where(
            BundlePurchase.invoice_payload == payload.invoice_payload,
            BundlePurchase.status == "pending",
        )
    )
    sub = res.scalars().first()
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    sub.status = "active"
    await db.commit()
    await db.refresh(sub)
    logger.info(f"Successfully confirmed bundle for user {sub.user_id}!")
    return {"status": "success"}


@router.post("/buy/")
async def buy_bundle(
    bundle: str = "bundle_1",
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Initiate a bundle purchase."""
    user_id = await resolve_user_id(tg_id, db)
    logger.info(f"Initiating bundle purchase for tg user {tg_id}")
    bundles_list = await bundles()
    bundle_data = next((p for p in bundles_list if p.id == bundle), None)
    if bundle_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bundle",
        )
    link, payload = export_tg_invoice(
        item_title=f"Wishes bundle ({bundle_data.title})",
        item_id=bundle,
        amount_stars=bundle_data.stars,
        item_description="Extra wishes for your immersion ✨",
    )

    sub = BundlePurchase(
        user_id=user_id, bundle=bundle, status="pending", invoice_payload=payload
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
