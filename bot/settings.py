from environs import Env
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                        "(%(filename)s).%(funcName)s(%(lineno)d) -%(message)s")


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    app_url: str
    debug: bool


@dataclass
class LLM:
    provider: str
    model: str
    temperature: float
    top_p: float
    openai_api_key: str
    google_api_key: str


@dataclass
class Settings:
    bots: Bots
    llm: LLM


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TG_BOT_TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            app_url=env.str("APP_URL", "http://app:8000"),
            debug=env.bool("DEBUG", False)
        ),
    )


settings = get_settings('.env')
print(settings)
