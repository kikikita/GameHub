from pydantic_settings import BaseSettings
import logging
from pydantic import SecretStr


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(asctime)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)


class BaseAppSettings(BaseSettings):
    """Base settings class with common configuration."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class AppSettings(BaseAppSettings):
    tg_bot_token: SecretStr
    server_auth_token: SecretStr
    debug: bool = False
    database_url: str
    gemini_api_keys: SecretStr | None = None
    redis_url: str = "redis://redis"
    top_p: float = 0.95
    temperature: float = 0.5
    pregenerate_next_scene: bool = True
    request_timeout: int = 20
    bot_server_url: str = "http://bot:7000"
    admin_ids: list[int] = []

    # Cost in wishes to create a custom story
    create_story_cost: int = 5

    # Path to JSON file with default preset worlds and stories
    presets_file_path: str = "/app/stories/golden_set.json"

    tg_payment_provider_token: SecretStr | None = None      # @BotFather → “Payment” tab
    tg_payment_currency: str = "XTR"           # Stars’ pseudo-currency code
    tg_webapp_bot_username: str = "@aimmersia_bot"               


settings = AppSettings()
