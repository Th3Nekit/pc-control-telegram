"""Middleware для ограничения доступа только владельцу бота."""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

log = logging.getLogger(__name__)


class OwnerOnlyMiddleware(BaseMiddleware):
    """Пропускает только сообщения и callback'и от OWNER_ID."""

    def __init__(self, owner_id: int) -> None:
        self._owner_id = owner_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int | None = None
        if isinstance(event, (Message, CallbackQuery)) and event.from_user is not None:
            user_id = event.from_user.id

        if user_id != self._owner_id:
            if user_id is not None:
                log.warning("Unauthorized access attempt from user_id=%s", user_id)
            return None

        return await handler(event, data)
