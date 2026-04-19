"""Процессы: список, завершение, запуск, очистка корзины."""
from __future__ import annotations

import os

import psutil
import winshell
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_menu
from utils import run_sync, safe_handler

router = Router(name="tasks")

MAX_MESSAGE = 3500


def _collect_tasks() -> list[str]:
    rows: list[str] = []
    for proc in psutil.process_iter(["pid", "name", "username"]):
        info = proc.info
        rows.append(
            f"<code>{info['pid']:>6}</code>  {info.get('name') or '?'}"
            + (f"  · {info['username']}" if info.get("username") else "")
        )
    return rows


@router.message(Command("tasks"))
@router.callback_query(F.data == "menu:tasks")
@safe_handler
async def cmd_tasks(event: Message | CallbackQuery) -> None:
    rows = await run_sync(_collect_tasks)
    if not rows:
        text = "Процессы не найдены."
        if isinstance(event, CallbackQuery):
            await event.answer(text)
            return
        await event.answer(text)
        return

    chunks: list[str] = []
    buf = "<b>📝 Процессы</b>\n\n"
    for row in rows:
        if len(buf) + len(row) + 1 > MAX_MESSAGE:
            chunks.append(buf)
            buf = ""
        buf += row + "\n"
    chunks.append(buf)

    target = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer()
    for i, chunk in enumerate(chunks):
        markup = back_to_menu() if i == len(chunks) - 1 else None
        await target.answer(chunk, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.message(Command("killall"))
@safe_handler
async def cmd_killall(msg: Message) -> None:
    def _kill() -> int:
        killed = 0
        protect = {
            "explorer.exe", "cmd.exe", "python.exe", "pythonw.exe",
            "svchost.exe", "wininit.exe", "csrss.exe", "smss.exe",
            "lsass.exe", "winlogon.exe", "services.exe", "system",
        }
        me = psutil.Process().pid
        for p in psutil.process_iter(["pid", "name"]):
            name = (p.info.get("name") or "").lower()
            if p.info["pid"] == me or name in protect:
                continue
            try:
                p.kill()
                killed += 1
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return killed

    count = await run_sync(_kill)
    await msg.answer(f"☠️ Закрыто процессов: <b>{count}</b>", parse_mode=ParseMode.HTML)


@router.message(Command("close"))
@safe_handler
async def cmd_close(msg: Message, command: CommandObject) -> None:
    if not command.args:
        await msg.answer("Использование: <code>/close имя.exe</code>", parse_mode=ParseMode.HTML)
        return
    name = command.args.strip().lower()

    def _close() -> int:
        killed = 0
        for p in psutil.process_iter(["name"]):
            if (p.info.get("name") or "").lower() == name:
                try:
                    p.kill()
                    killed += 1
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        return killed

    count = await run_sync(_close)
    if count:
        await msg.answer(f"✅ Закрыто экземпляров <b>{name}</b>: {count}", parse_mode=ParseMode.HTML)
    else:
        await msg.answer(f"⚠️ Процесс <b>{name}</b> не найден.", parse_mode=ParseMode.HTML)


@router.message(Command("open"))
@safe_handler
async def cmd_open(msg: Message, command: CommandObject) -> None:
    if not command.args:
        await msg.answer("Использование: <code>/open program.exe</code>", parse_mode=ParseMode.HTML)
        return
    target = command.args.strip()
    try:
        await run_sync(os.startfile, target)  # type: ignore[attr-defined]
    except OSError as exc:
        await msg.answer(f"⚠️ Не удалось запустить: <code>{exc}</code>", parse_mode=ParseMode.HTML)
        return
    await msg.answer(f"▶️ Запущено: <b>{target}</b>", parse_mode=ParseMode.HTML)


@router.message(Command("clearbin"))
@safe_handler
async def cmd_clearbin(msg: Message) -> None:
    def _empty() -> bool:
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return True
        except Exception:  # noqa: BLE001
            return False

    ok = await run_sync(_empty)
    if ok:
        await msg.answer("🗑 Корзина очищена.")
    else:
        await msg.answer("🗑 Корзина уже пуста.")
