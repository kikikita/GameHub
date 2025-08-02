from keyboards.inline import stories_keyboard
from settings import settings
from utils.i18n import t
import httpx

http_client = httpx.AsyncClient(base_url=settings.bots.app_url, timeout=10.0)


async def show_presets(chat_id: int, bot, lang: str) -> None:
    resp = await http_client.get("/api/v1/stories/preset/", params={"lang": lang})
    if resp.status_code != 200:
        await bot.send_message(chat_id, t(lang, "no_stories"))
        return
    stories = resp.json()
    emojis = {
        "Horror": "😱",
        "Romantic": "😍",
        "Adventure": "🏕️",
        "Fantasy": "🧙",
        "Sci-Fi": "🤖",
    }
    lines = [t(lang, "choose_story")]
    for s in stories:
        emoji = emojis.get(s.get("genre"), "🎲")
        genre = t(lang, f"genre_{s.get('genre')}") or s.get("genre")
        title = s.get("title")
        if isinstance(title, dict):
            title = title.get(lang) or title.get("en") or next(iter(title.values()), "")
        lines.append(f"{emoji} [{genre}] {title}")
    text = "\n".join(lines)
    kb = stories_keyboard(stories, settings.bots.web_url, lang)
    await bot.send_message(chat_id, text, reply_markup=kb)

