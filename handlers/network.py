"""Сеть: список Wi-Fi сетей и speedtest."""
from __future__ import annotations

import re
import subprocess

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import speedtest

from keyboards import back_to_menu
from utils import run_sync, safe_handler

router = Router(name="network")


def _list_wifi() -> list[dict[str, str]]:
    """Возвращает список сетей через `netsh wlan show networks mode=bssid`."""
    try:
        out = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            timeout=8,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

    # netsh в Windows RU выдаёт cp866 локаль, в EN — cp1252
    for encoding in ("cp866", "cp1251", "utf-8"):
        try:
            text = out.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = out.decode(errors="ignore")

    networks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    ssid_re = re.compile(r"^\s*SSID\s+\d+\s*:\s*(.*)$", re.IGNORECASE)
    signal_re = re.compile(r"^\s*(?:Сигнал|Signal)\s*:\s*(\d+)%", re.IGNORECASE)
    auth_re = re.compile(
        r"^\s*(?:Проверка\s+подлинности|Authentication)\s*:\s*(.+)$", re.IGNORECASE
    )

    for line in text.splitlines():
        ssid_match = ssid_re.match(line)
        if ssid_match:
            if current:
                networks.append(current)
            current = {"ssid": ssid_match.group(1).strip() or "(скрытая)"}
            continue

        signal_match = signal_re.match(line)
        if signal_match and current:
            current["signal"] = signal_match.group(1) + "%"

        auth_match = auth_re.match(line)
        if auth_match and current:
            current["auth"] = auth_match.group(1).strip()

    if current:
        networks.append(current)

    return networks


def _build_wifi_text(nets: list[dict[str, str]]) -> str:
    if not nets:
        return "📡 Сети не найдены или адаптер Wi-Fi выключен."

    nets.sort(key=lambda n: int(n.get("signal", "0").rstrip("%")), reverse=True)
    lines = ["<b>📡 Доступные сети</b>", ""]
    for net in nets:
        ssid = net.get("ssid", "?")
        signal = net.get("signal", "—")
        auth = net.get("auth", "—")
        lines.append(f"<b>{ssid}</b> — {signal}, {auth}")
    return "\n".join(lines)


def _run_speedtest() -> dict[str, float]:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = st.download() / 1_000_000
    up = st.upload() / 1_000_000
    ping = st.results.ping
    return {"down": down, "up": up, "ping": ping}


@router.message(Command("wifi"))
@router.callback_query(F.data == "menu:wifi")
@safe_handler
async def cmd_wifi(event: Message | CallbackQuery) -> None:
    target = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer("📡 Сканирую…")
    nets = await run_sync(_list_wifi)
    text = _build_wifi_text(nets)
    if target is not None:
        await target.answer(text, reply_markup=back_to_menu(), parse_mode=ParseMode.HTML)


@router.message(Command("speedtest"))
@router.callback_query(F.data == "menu:speedtest")
@safe_handler
async def cmd_speedtest(event: Message | CallbackQuery) -> None:
    target = event.message if isinstance(event, CallbackQuery) else event
    if target is None:
        return

    if isinstance(event, CallbackQuery):
        await event.answer("🚀 Замер скорости, подождите…", show_alert=False)

    notice = await target.answer("🚀 Замеряю скорость… это займёт ~20 секунд.")
    result = await run_sync(_run_speedtest)

    text = (
        "<b>🚀 Speedtest</b>\n\n"
        f"<b>Скачивание:</b> {result['down']:.2f} Мбит/с\n"
        f"<b>Отдача:</b>      {result['up']:.2f} Мбит/с\n"
        f"<b>Пинг:</b>        {result['ping']:.0f} мс"
    )
    try:
        await notice.edit_text(text, reply_markup=back_to_menu(), parse_mode=ParseMode.HTML)
    except Exception:  # noqa: BLE001
        await target.answer(text, reply_markup=back_to_menu(), parse_mode=ParseMode.HTML)
