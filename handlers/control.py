"""Удалённое управление курсором через inline-клавиатуру."""
from __future__ import annotations

import pyautogui
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards import control_pad
from utils import run_sync, safe_handler

router = Router(name="control")

pyautogui.FAILSAFE = False

# Состояние шага на пользователя не завязано: бот работает для одного владельца.
_STEP: dict[str, int] = {"px": 25}

CONTROL_TEXT = (
    "<b>🖱 Управление курсором</b>\n\n"
    "Стрелки перемещают мышь на <b>{step}</b> пикселей.\n"
    "Нажмите «🖱» для клика, «🖱🖱» для двойного, «🖱R» — правый клик.\n"
    "Кнопки «Шаг ×N» меняют скорость перемещения."
)


@router.message(Command("control"))
@router.callback_query(F.data == "menu:control")
@safe_handler
async def cmd_control(event: Message | CallbackQuery) -> None:
    text = CONTROL_TEXT.format(step=_STEP["px"])
    target = event.message if isinstance(event, CallbackQuery) else event
    if target is None:
        return
    if isinstance(event, CallbackQuery):
        await event.answer()
        await target.edit_text(text, reply_markup=control_pad(), parse_mode=ParseMode.HTML)
    else:
        await target.answer(text, reply_markup=control_pad(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("ctl:"))
@safe_handler
async def cb_control(cb: CallbackQuery) -> None:
    assert cb.data is not None
    parts = cb.data.split(":")
    action = parts[1]
    step = _STEP["px"]

    if action == "up":
        await run_sync(pyautogui.moveRel, 0, -step)
    elif action == "down":
        await run_sync(pyautogui.moveRel, 0, step)
    elif action == "left":
        await run_sync(pyautogui.moveRel, -step, 0)
    elif action == "right":
        await run_sync(pyautogui.moveRel, step, 0)
    elif action == "click":
        await run_sync(pyautogui.click)
    elif action == "double":
        await run_sync(pyautogui.doubleClick)
    elif action == "rclick":
        await run_sync(pyautogui.rightClick)
    elif action == "step" and len(parts) > 2:
        try:
            _STEP["px"] = max(1, int(parts[2]))
        except ValueError:
            pass
        if cb.message is not None:
            try:
                await cb.message.edit_text(
                    CONTROL_TEXT.format(step=_STEP["px"]),
                    reply_markup=control_pad(),
                    parse_mode=ParseMode.HTML,
                )
            except Exception:  # noqa: BLE001
                pass
    await cb.answer()
