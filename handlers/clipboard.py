"""Буфер обмена: получить и установить."""
from __future__ import annotations

import pyperclip
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_menu
from utils import run_sync, safe_handler

router = Router(name="clipboard")

MAX_LEN = 3500


@router.message(Command("clip", "clipboard"))
@router.callback_query(F.data == "menu:clipboard")
@safe_handler
async def cmd_clip(event: Message | CallbackQuery) -> None:
    data = await run_sync(pyperclip.paste)
    target = event.message if isinstance(event, CallbackQuery) else event

    if isinstance(event, CallbackQuery):
        await event.answer()

    if target is None:
        return

    if not data:
        await target.answer("📋 Буфер обмена пуст.", reply_markup=back_to_menu())
        return

    if len(data) > MAX_LEN:
        data = data[:MAX_LEN] + "\n…(обрезано)"

    await target.answer(
        f"📋 <b>Буфер обмена</b>\n<code>{_escape(data)}</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_menu(),
    )


@router.message(Command("setclip", "setclipboard"))
@safe_handler
async def cmd_setclip(msg: Message, command: CommandObject) -> None:
    if not command.args:
        await msg.answer("Использование: <code>/setclip текст</code>", parse_mode=ParseMode.HTML)
        return
    await run_sync(pyperclip.copy, command.args)
    await msg.answer("✍️ Буфер обмена обновлён.")


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
