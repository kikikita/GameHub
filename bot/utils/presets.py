from keyboards.inline import stories_keyboard
from settings import settings
from utils.i18n import t
import httpx

http_client = httpx.AsyncClient(base_url=settings.bots.app_url, timeout=10.0)


def genre_key(raw_genre: str) -> str:
    if not raw_genre:
        return ""
    return ''.join(word.capitalize() for word in raw_genre.replace('-', ' ').replace('_', ' ').split())


async def show_presets(chat_id: int, bot, lang: str) -> None:
    resp = await http_client.get("/api/v1/stories/preset/", params={"lang": lang})
    if resp.status_code != 200:
        await bot.send_message(chat_id, t(lang, "no_stories"))
        return
    stories = resp.json()
    emojis = {
        "Horror": "😱",
        "Romantic": "😍",
        "Adventure": "🏰",
        "Fantasy": "🧙",
        "SciFi": "🤖",
        "Detective": "🕵️",
        "Mystery": "🕯",
        "Drama": "🎭",
        "Comedy": "😂",
        "Action": "⚔️",
        "Thriller": "😨",
        "Historical": "🏺",
        "Western": "🤠",
        "Superhero": "🦸‍♂️",
        "SliceOfLife": "🌸",
        "Survival": "🏝",
        "Steampunk": "⚙️",
        "Cyberpunk": "🌃",
        "PostApocalyptic": "☢️",
        "Space": "🚀",
        "Sports": "🏆",
        "Crime": "🔪"
    }
    lines = [f"<b>{t(lang, "choose_story")}</b>"]
    for s in stories:
        gkey = genre_key(s.get("genre", ""))
        emoji = emojis.get(gkey, "🎲")
        genre = t(lang, f"genre_{gkey}") or s.get("genre")
        title = s.get("title")
        if isinstance(title, dict):
            title = title.get(lang) or title.get("en") or next(iter(title.values()), "")
        desc = s.get("story_desc")
        if isinstance(desc, dict):
            desc = desc.get(lang) or desc.get("en") or next(iter(desc.values()), "")
        entry = f"{emoji} [{genre}] {title}"
        if desc:
            entry = f"{entry}\n{desc}"
        lines.append(entry)
    text = "\n\n".join(lines)
    kb = stories_keyboard(stories, settings.bots.web_url, lang)
    await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
