"""Точка входа: настройка → запуск бота."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Settings, env_exists, load_settings
from handlers import register_all
from security import OwnerOnlyMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pc-control")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pc-control-bot",
        description="Telegram-бот для управления Windows-ПК.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Открыть окно настроек и выйти.",
    )
    return parser.parse_args()


def run_setup() -> None:
    from gui import launch_settings_window

    launch_settings_window()


async def run_bot(settings: Settings) -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp["settings"] = settings

    # Middleware на уровне observer: фильтрует всё до входа в роутеры.
    owner_guard = OwnerOnlyMiddleware(settings.owner_id)
    dp.message.middleware(owner_guard)
    dp.callback_query.middleware(owner_guard)

    register_all(dp)

    log.info("Starting bot for owner_id=%s", settings.owner_id)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def main() -> int:
    args = parse_args()

    if args.setup:
        run_setup()
        return 0

    settings = load_settings()
    if settings is None:
        if env_exists():
            log.error(
                "Файл .env существует, но BOT_TOKEN или OWNER_ID заполнены некорректно. "
                "Запусти с --setup для редактирования."
            )
        else:
            log.info("Файл .env не найден, открываю окно настроек.")
        run_setup()
        settings = load_settings()

    if settings is None:
        log.error("Настройки не заполнены. Выход.")
        return 1

    try:
        asyncio.run(run_bot(settings))
    except (KeyboardInterrupt, SystemExit):
        log.info("Остановлено пользователем.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
