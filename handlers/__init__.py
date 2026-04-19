"""Регистрация всех роутеров в главном диспетчере."""
from __future__ import annotations

from aiogram import Dispatcher

from . import (
    clipboard,
    control,
    network,
    power,
    screen,
    start,
    system,
    tasks,
    weather,
)


def register_all(dp: Dispatcher) -> None:
    for module in (start, system, power, tasks, screen, clipboard, network, weather, control):
        dp.include_router(module.router)
