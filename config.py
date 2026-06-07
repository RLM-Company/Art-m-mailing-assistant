"""
Конфигурация бота. Все настройки берутся из .env файла.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    activation_token: str
    db_path: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "сюда_вставь_токен_бота":
        raise RuntimeError(
            "BOT_TOKEN не задан. Скопируй .env.example в .env и впиши токен от @BotFather."
        )

    return Config(
        bot_token=bot_token,
        activation_token=os.getenv("ACTIVATION_TOKEN", "Sgakbw12ajjananoa1"),
        db_path=os.getenv("DB_PATH", "bot.db"),
    )


config = load_config()
