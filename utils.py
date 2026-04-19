"""Утилиты: форматирование, async-обёртка sync функций, декоратор ошибок."""
from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

from aiogram.types import CallbackQuery, Message

log = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def format_bytes(size: float, suffix: str = "Б") -> str:
    """Преобразует байты в человекочитаемую строку: 1.23 ГБ."""
    for unit in ("", "К", "М", "Г", "Т", "П"):
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}{suffix}"
        size /= 1024.0
    return f"{size:.2f} Э{suffix}"


async def run_sync(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    """Запускает синхронную функцию в пуле, не блокируя event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


def safe_handler(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Логирует исключения из хэндлера и сообщает о них пользователю."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            log.exception("Handler %s failed", func.__name__)
            for arg in args:
                if isinstance(arg, Message):
                    try:
                        await arg.answer(f"⚠️ Ошибка: <code>{exc}</code>")
                    except Exception:  # noqa: BLE001
                        pass
                    break
                if isinstance(arg, CallbackQuery):
                    try:
                        await arg.answer(f"⚠️ {exc}", show_alert=True)
                    except Exception:  # noqa: BLE001
                        pass
                    break
            return None

    return wrapper
