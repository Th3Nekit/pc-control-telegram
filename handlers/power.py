"""Питание: блокировка, сон, выключение, таймеры."""
from __future__ import annotations

import os
import subprocess

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_menu, power_menu
from utils import run_sync, safe_handler

router = Router(name="power")


POWER_TEXT = (
    "<b>⚡ Меню питания</b>\n\n"
    "Выберите действие. Таймер можно отменить кнопкой "
    "<i>«Отменить таймер»</i> до срабатывания."
)


def _shell(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=False, timeout=10)


@router.message(Command("lock"))
@safe_handler
async def cmd_lock(msg: Message) -> None:
    await run_sync(_shell, "rundll32.exe user32.dll,LockWorkStation")
    await msg.answer("🔒 Экран заблокирован.")


@router.callback_query(F.data == "menu:lock")
@safe_handler
async def cb_lock(cb: CallbackQuery) -> None:
    await run_sync(_shell, "rundll32.exe user32.dll,LockWorkStation")
    await cb.answer("🔒 Заблокировано", show_alert=False)


@router.message(Command("power"))
@safe_handler
async def cmd_power(msg: Message, command: CommandObject) -> None:
    """Поддерживает /power и /power <sub> для обратной совместимости."""
    if not command.args:
        await msg.answer(POWER_TEXT, reply_markup=power_menu(), parse_mode=ParseMode.HTML)
        return

    parts = command.args.split()
    action = parts[0].lower()
    await _handle_power_action(msg, action, parts[1:])


@router.callback_query(F.data == "menu:power")
@safe_handler
async def cb_power(cb: CallbackQuery) -> None:
    if cb.message is not None:
        await cb.message.edit_text(POWER_TEXT, reply_markup=power_menu(), parse_mode=ParseMode.HTML)
    await cb.answer()


@router.callback_query(F.data.startswith("power:"))
@safe_handler
async def cb_power_action(cb: CallbackQuery) -> None:
    assert cb.data is not None
    parts = cb.data.split(":")
    action = parts[1]
    extra = parts[2:]
    await _handle_power_action(cb, action, extra)


async def _handle_power_action(
    event: Message | CallbackQuery, action: str, args: list[str]
) -> None:
    async def reply(text: str) -> None:
        if isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)

    if action == "sleep":
        await run_sync(_shell, "rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        await reply("💤 Перевожу в спящий режим.")
    elif action == "hibernate":
        await run_sync(_shell, "shutdown /h")
        await reply("❄️ Гибернация.")
    elif action == "restart":
        await reply("🔁 Перезагрузка.")
        await run_sync(_shell, "shutdown /r /t 0")
    elif action == "shutdown":
        await reply("⛔ Выключение.")
        await run_sync(_shell, "shutdown /s /t 0")
    elif action == "cancel":
        await run_sync(_shell, "shutdown /a")
        await reply("✖️ Таймер выключения отменён.")
    elif action == "timer":
        minutes = _parse_timer(args)
        if minutes is None:
            await reply("Укажи число минут: /power timer 15")
            return
        await run_sync(_shell, f"shutdown /s /t {minutes * 60}")
        await reply(f"⏱ Таймер: выключение через {minutes} мин.")
    else:
        await reply(
            "Доступно: sleep, restart, shutdown, hibernate, timer <минут>, cancel"
        )


def _parse_timer(args: list[str]) -> int | None:
    if not args:
        return None
    try:
        value = int(args[0])
    except ValueError:
        return None
    return value if value > 0 else None
