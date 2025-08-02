import uuid
import requests
from src.config import settings
import logging

logger = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{settings.tg_bot_token.get_secret_value()}"


def export_tg_invoice(
    item_title: str, item_id: str, amount_stars: int, item_description: str
) -> str:
    payload = f"{item_id}:{uuid.uuid4()}"
    resp = requests.post(
        f"{BOT_API}/createInvoiceLink",
        json={
            "title": item_title,
            "description": item_description,
            "payload": payload,
            "recurring": True,
            "provider_token": "",  # empty for telegram stars
            "currency": settings.tg_payment_currency,
            "prices": [{"label": item_id, "amount": amount_stars}],
        },
    ).json()
    if not resp["ok"]:
        logger.error(resp)
        raise RuntimeError("Telegram exportInvoice failed")
    return resp["result"], payload
