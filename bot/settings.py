"""Configuration loader for the bot."""

import logging
from dataclasses import dataclass
from typing import List

from environs import Env
from pydantic import SecretStr

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - [%(levelname)s] - %(name)s - "
        "(%(filename)s).%(funcName)s(%(lineno)d) -%(message)s"
    ),
)


@dataclass
class Bots:
    """Telegram bot settings."""

    bot_token: SecretStr
    server_auth_token: SecretStr
    admin_id: List[int]
    app_url: str
    web_url: str
    debug: bool


@dataclass
class Settings:
    """Application settings container."""

    bots: Bots
    create_story_cost: int


def get_settings(path: str) -> Settings:
    """Load settings from a .env file."""

    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=SecretStr(env.str("TG_BOT_TOKEN")),
            server_auth_token=SecretStr(env.str("SERVER_AUTH_TOKEN")),
            admin_id=[int(x) for x in env.list("ADMIN_ID")],
            app_url=env.str("APP_URL", "http://highway:8000"),
            web_url=env.str("WEB_URL", "https://app.immersia.fun/"),
            debug=env.bool("DEBUG", False)
        ),
        create_story_cost=env.int("CREATE_STORY_COST", 5),
    )


settings = get_settings(".env")
