"""Configuration loader for the bot."""

import logging
from dataclasses import dataclass

from environs import Env

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

    bot_token: str
    admin_id: int
    app_url: str
    debug: bool


@dataclass
class Settings:
    """Application settings container."""

    bots: Bots


def get_settings(path: str) -> Settings:
    """Load settings from a .env file."""

    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TG_BOT_TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            app_url=env.str("APP_URL", "http://highway:8000"),
            debug=env.bool("DEBUG", False)
        ),
    )


settings = get_settings(".env")
