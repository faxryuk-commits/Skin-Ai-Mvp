import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class BotSettings:
    token: str
    api_base_url: str
    privacy_disclaimer: str
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None


def get_settings() -> BotSettings:
    token = os.getenv("BOT_TOKEN", "")
    api_base = os.getenv("API_BASE_URL", "").rstrip("/")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN в переменных окружения.")
    if not api_base:
        raise RuntimeError("Не найден API_BASE_URL в переменных окружения.")

    privacy_disclaimer = (
        "Отправляя фото, ты подтверждаешь, что тебе 16+ и даёшь согласие "
        "на обработку изображения для анализа. Мы не храним фото без явного согласия."
    )

    return BotSettings(
        token=token,
        api_base_url=api_base,
        privacy_disclaimer=privacy_disclaimer,
        terms_url=os.getenv("TERMS_URL"),
        privacy_url=os.getenv("PRIVACY_URL"),
    )

