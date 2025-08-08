from aiogram import Router
from aiogram import types
from aiogram import F
import httpx
from settings import settings
import logging

logger = logging.getLogger(__name__)

router = Router()

http_client = httpx.AsyncClient(
    base_url=settings.bots.app_url,
    timeout=httpx.Timeout(60.0),
    headers={
        "X-Server-Auth": settings.bots.server_auth_token.get_secret_value()
    },
)


async def notify_service(msg: types.Message, item: str, success: bool = True) -> None:
    """Send a purchase notification to the service chat."""
    user = msg.from_user
    username = f"@{user.username}" if user.username else user.full_name
    amount = msg.successful_payment.total_amount
    currency = msg.successful_payment.currency
    title = "💸 <b>New purchase</b>" if success else "❌ <b>Purchase failed</b>"
    text = (
        f"{title}\n"
        f"👤 {username} (id: {user.id})\n"
        f"📦 {item}\n"
        f"💰 {amount} {currency} ({amount / 100}$)"
    )
    await msg.bot.send_message(settings.bots.service_chat, text, parse_mode="HTML")


@router.pre_checkout_query()
async def pre_checkout(pcq: types.PreCheckoutQuery):
    if pcq.invoice_payload.startswith("wishes"):
        await wishes_pre_checkout(pcq)
    else:
        await subscription_pre_checkout(pcq)


async def subscription_pre_checkout(pcq: types.PreCheckoutQuery):
    resp = await http_client.post("/api/v1/subscription/verify/", json={"invoice_payload": pcq.invoice_payload})

    is_ok = resp.json().get("status") == "success"
    logger.info(f"Pre-checkout query {pcq.id} verified, is_ok: {is_ok}")

    await pcq.answer(
        ok=is_ok,
        error_message=(
            "Aliens tried to steal your card's CVV,"
            " but we successfully protected your credentials,"
            " try to pay again in a few minutes, we need a small rest."
        ),
    )


async def wishes_pre_checkout(pcq: types.PreCheckoutQuery):
    resp = await http_client.post("/api/v1/wishes/verify/", json={"invoice_payload": pcq.invoice_payload})

    is_ok = resp.json().get("status") == "success"
    logger.info(f"Pre-checkout query {pcq.id} verified, is_ok: {is_ok}")

    await pcq.answer(
        ok=is_ok,
        error_message=(
            "Aliens tried to steal your card's CVV,"
            " but we successfully protected your credentials,"
            " try to pay again in a few minutes, we need a small rest."
        ),
    )


@router.message(F.successful_payment)
async def paid(msg: types.Message):
    logger.info(f"Incoming confirmation for payment for user {msg.from_user.id}")

    if msg.successful_payment.invoice_payload.startswith("wishes"):
        await wishes_paid(msg)
    else:
        await subscription_paid(msg)


async def wishes_paid(msg: types.Message):
    logger.info(f"Incoming confirmation for payment for user {msg.from_user.id}")
    resp = await http_client.post("/api/v1/wishes/confirm/", json={"invoice_payload": msg.successful_payment.invoice_payload})
    if resp.json().get("status") != "success":
        logger.error(f"Failed to confirm payment for {msg.from_user.id}! {resp}")
        await msg.answer(
            "Something went wrong with your payment. Please contact our support 🙏",
            parse_mode="Markdown",
        )
        bundle_id = msg.successful_payment.invoice_payload.split(":", 1)[0]
        pretty = bundle_id.replace("_", " ").title()
        await notify_service(msg, f"Wishes bundle: {pretty}", success=False)
    else:
        logger.info(f"Payment confirmed for {msg.from_user.id}!")
        await msg.answer(
            "Hoooooray! Thanks for payment! We will proceed your order for `{} {}`"
            " as fast as possible! Stay in touch.".format(
                msg.successful_payment.total_amount,
                msg.successful_payment.currency,
            ),
            parse_mode="Markdown",
        )
        bundle_id = msg.successful_payment.invoice_payload.split(":", 1)[0]
        pretty = bundle_id.replace("_", " ").title()
        await notify_service(msg, f"Wishes bundle: {pretty}")


async def subscription_paid(msg: types.Message):
    resp = await http_client.post("/api/v1/subscription/confirm/", json={"invoice_payload": msg.successful_payment.invoice_payload})
    if resp.json().get("status") != "success":
        logger.error(f"Failed to confirm payment for {msg.from_user.id}! {resp}")
        await msg.answer(
            "Something went wrong with your payment. Please contact our support 🙏",
            parse_mode="Markdown",
        )
        plan_id = msg.successful_payment.invoice_payload.split(":", 1)[0]
        pretty = plan_id.replace("_", " ").title()
        await notify_service(msg, f"Subscription plan: {pretty}", success=False)
    else:
        logger.info(f"Payment confirmed for {msg.from_user.id}!")
        await msg.answer(
            "Hoooooray! Thanks for payment! We will proceed your order for `{} {}`"
            " as fast as possible! Stay in touch.".format(
                msg.successful_payment.total_amount,
                msg.successful_payment.currency,
            ),
            parse_mode="Markdown",
        )
        plan_id = msg.successful_payment.invoice_payload.split(":", 1)[0]
        pretty = plan_id.replace("_", " ").title()
        await notify_service(msg, f"Subscription plan: {pretty}")
