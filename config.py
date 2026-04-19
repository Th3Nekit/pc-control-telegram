"""Загрузка и сохранение настроек приложения в .env рядом с main.py."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, set_key

BASE_DIR: Path = Path(__file__).resolve().parent
ENV_PATH: Path = BASE_DIR / ".env"


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    owner_id: int
    weather_api_key: Optional[str]
    city: Optional[str]

    @property
    def weather_enabled(self) -> bool:
        return bool(self.weather_api_key and self.city)


def load_settings() -> Optional[Settings]:
    """Возвращает настройки, если заполнены обязательные поля. Иначе None."""
    import os

    load_dotenv(ENV_PATH, override=True)

    token = (os.getenv("BOT_TOKEN") or "").strip()
    owner = (os.getenv("OWNER_ID") or "").strip()

    if not token or not owner.isdigit():
        return None

    return Settings(
        bot_token=token,
        owner_id=int(owner),
        weather_api_key=(os.getenv("WEATHER_API_KEY") or "").strip() or None,
        city=(os.getenv("CITY") or "").strip() or None,
    )


def save_settings(
    bot_token: str,
    owner_id: int,
    weather_api_key: str = "",
    city: str = "",
) -> None:
    """Записывает настройки в .env."""
    ENV_PATH.touch(exist_ok=True)
    path = str(ENV_PATH)
    set_key(path, "BOT_TOKEN", bot_token.strip())
    set_key(path, "OWNER_ID", str(int(owner_id)))
    set_key(path, "WEATHER_API_KEY", weather_api_key.strip())
    set_key(path, "CITY", city.strip())


def env_exists() -> bool:
    return ENV_PATH.exists()
