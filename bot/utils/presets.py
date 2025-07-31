from keyboards.inline import stories_keyboard
from settings import settings
import httpx

http_client = httpx.AsyncClient(base_url=settings.bots.app_url, timeout=10.0)


async def show_presets(chat_id: int, bot, headers: dict) -> None:
    resp = await http_client.get("/api/v1/stories/preset", headers=headers)
    if resp.status_code != 200:
        await bot.send_message(chat_id, "Нет доступных историй")
        return
    stories = resp.json()
    emojis = {
        "Horror": "😱",
        "Romantic": "😍",
        "Adventure": "🏕️",
        "Fantasy": "🧙",
        "Sci-Fi": "🤖",
    }
    lines = ["Выберите вашу историю:"]
    for s in stories:
        emoji = emojis.get(s.get("genre"), "🎲")
        lines.append(f"{emoji} [{s.get('genre')}] {s.get('title')}")
    text = "\n".join(lines)
    kb = stories_keyboard(stories, settings.bots.web_url)
    await bot.send_message(chat_id, text, reply_markup=kb)

