"""Характеристики и нагрузка системы."""
from __future__ import annotations

import platform
import subprocess

import cpuinfo
import psutil
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_menu
from utils import format_bytes, run_sync, safe_handler

router = Router(name="system")


def _nvidia_info() -> str:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            timeout=5,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return "не определена (нужен Nvidia GPU)"
    text = out.decode(errors="ignore").strip()
    if not text:
        return "не определена"
    name, temp, util = [p.strip() for p in text.split(",")]
    return f"{name} — {temp}°C / {util}%"


def _build_checkpc() -> str:
    cpu = cpuinfo.get_cpu_info().get("brand_raw", "неизвестно")
    vm = psutil.virtual_memory()
    freq = psutil.cpu_freq()
    freq_str = f"{freq.current / 1000:.2f} ГГц" if freq else "—"
    return (
        "<b>💻 Характеристики ПК</b>\n\n"
        f"<b>ОС:</b> {platform.system()} {platform.release()}\n"
        f"<b>Процессор:</b> {cpu}\n"
        f"<b>Частота:</b> {freq_str}\n"
        f"<b>Ядер:</b> {psutil.cpu_count(logical=True)} "
        f"({psutil.cpu_count(logical=False)} физических)\n"
        f"<b>ОЗУ:</b> {format_bytes(vm.total)} всего, "
        f"{format_bytes(vm.used)} занято, {format_bytes(vm.available)} свободно\n"
        f"<b>GPU:</b> {_nvidia_info()}"
    )


def _build_performance() -> str:
    cpu_percent = psutil.cpu_percent(interval=0.8)
    vm = psutil.virtual_memory()
    return (
        "<b>📊 Нагрузка</b>\n\n"
        f"<b>Процессор:</b> {cpu_percent:.1f}%\n"
        f"<b>ОЗУ:</b> {vm.percent:.1f}% "
        f"({format_bytes(vm.used)} / {format_bytes(vm.total)})\n"
        f"<b>GPU:</b> {_nvidia_info()}"
    )


def _build_disks() -> str:
    lines = ["<b>💽 Диски</b>", ""]
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue
        lines.append(
            f"<b>{part.device}</b> ({part.mountpoint})\n"
            f"  {format_bytes(usage.used)} / {format_bytes(usage.total)} "
            f"({usage.percent}%)"
        )
    return "\n".join(lines)


async def _reply(target: Message | CallbackQuery, text: str) -> None:
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.edit_text(text, reply_markup=back_to_menu(), parse_mode=ParseMode.HTML)
        await target.answer()
    else:
        await target.answer(text, reply_markup=back_to_menu(), parse_mode=ParseMode.HTML)


@router.message(Command("checkpc"))
@router.callback_query(F.data == "menu:checkpc")
@safe_handler
async def cmd_checkpc(event: Message | CallbackQuery) -> None:
    text = await run_sync(_build_checkpc)
    await _reply(event, text)


@router.message(Command("performance"))
@router.callback_query(F.data == "menu:performance")
@safe_handler
async def cmd_performance(event: Message | CallbackQuery) -> None:
    text = await run_sync(_build_performance)
    await _reply(event, text)


@router.message(Command("disks"))
@router.callback_query(F.data == "menu:disks")
@safe_handler
async def cmd_disks(event: Message | CallbackQuery) -> None:
    text = await run_sync(_build_disks)
    await _reply(event, text)
