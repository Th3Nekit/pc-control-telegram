"""Скриншоты и яркость экрана."""
from __future__ import annotations

import io

import mss
import mss.tools as mtools
import screen_brightness_control as sbc
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from keyboards import brightness_menu
from utils import run_sync, safe_handler

router = Router(name="screen")


def _capture_monitors() -> list[tuple[str, bytes]]:
    results: list[tuple[str, bytes]] = []
    with mss.mss() as sct:
        # sct.monitors[0] — виртуальный экран (сумма всех), отдельно не нужен
        for i, monitor in enumerate(sct.monitors[1:], start=1):
            img = sct.grab(monitor)
            png = mtools.to_png(img.rgb, img.size)
            results.append((f"monitor_{i}.png", png))
    return results


@router.message(Command("screenshot"))
@router.callback_query(F.data == "menu:screenshot")
@safe_handler
async def cmd_screenshot(event: Message | CallbackQuery) -> None:
    shots = await run_sync(_capture_monitors)
    target = event.message if isinstance(event, CallbackQuery) else event
    if target is None:
        return

    if isinstance(event, CallbackQuery):
        await event.answer("📷 Делаю скриншот…")

    if not shots:
        await target.answer("Не удалось получить монитор.")
        return

    for filename, data in shots:
        await target.answer_photo(
            BufferedInputFile(data, filename=filename),
            caption=f"📷 {filename}",
        )


@router.message(Command("brightness"))
@safe_handler
async def cmd_brightness(msg: Message, command: CommandObject) -> None:
    if not command.args:
        await msg.answer(
            "Текущая яркость: <b>{}%</b>\nИспользуйте: <code>/brightness 0-100</code>".format(
                _current_brightness()
            ),
            reply_markup=brightness_menu(),
            parse_mode=ParseMode.HTML,
        )
        return
    try:
        value = int(command.args.strip())
    except ValueError:
        await msg.answer("Значение должно быть числом от 0 до 100.")
        return
    await _set_brightness(msg, value)


@router.callback_query(F.data == "menu:brightness")
@safe_handler
async def cb_brightness(cb: CallbackQuery) -> None:
    if cb.message is not None:
        await cb.message.edit_text(
            f"☀️ <b>Яркость</b>\nТекущая: <b>{_current_brightness()}%</b>",
            reply_markup=brightness_menu(),
            parse_mode=ParseMode.HTML,
        )
    await cb.answer()


@router.callback_query(F.data.startswith("br:"))
@safe_handler
async def cb_set_brightness(cb: CallbackQuery) -> None:
    assert cb.data is not None
    value = int(cb.data.split(":")[1])
    await run_sync(sbc.set_brightness, value)
    await cb.answer(f"Яркость: {value}%")


async def _set_brightness(msg: Message, value: int) -> None:
    if not 0 <= value <= 100:
        await msg.answer("Яркость должна быть от 0 до 100.")
        return
    await run_sync(sbc.set_brightness, value)
    await msg.answer(f"☀️ Яркость: <b>{value}%</b>", parse_mode=ParseMode.HTML)


def _current_brightness() -> int:
    try:
        values = sbc.get_brightness()
        if isinstance(values, list) and values:
            return int(values[0])
        if isinstance(values, int):
            return values
    except Exception:  # noqa: BLE001
        pass
    return -1
