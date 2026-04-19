"""Главное меню, /start, /help."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from config import Settings
from keyboards import main_menu
from utils import safe_handler

router = Router(name="start")


WELCOME = (
    "👋 <b>PC Control Bot</b>\n\n"
    "Управляй своим компьютером прямо из Telegram.\n"
    "Выбери пункт меню или используй /help для полного списка команд."
)

HELP = (
    "<b>📖 Список команд</b>\n\n"
    "<b>Система</b>\n"
    "/checkpc — характеристики ПК\n"
    "/performance — нагрузка CPU / RAM / GPU\n"
    "/disks — статус дисков\n\n"
    "<b>Управление</b>\n"
    "/lock — заблокировать экран\n"
    "/power — меню питания\n"
    "/screenshot — скриншоты всех мониторов\n"
    "/brightness <code>0-100</code> — яркость\n"
    "/control — управление курсором\n\n"
    "<b>Процессы</b>\n"
    "/tasks — список процессов\n"
    "/killall — закрыть все пользовательские\n"
    "/open <code>program.exe</code> — запустить\n"
    "/close <code>имя.exe</code> — закрыть\n"
    "/clearbin — очистить корзину\n\n"
    "<b>Буфер обмена</b>\n"
    "/clip — получить содержимое\n"
    "/setclip <code>текст</code> — записать\n\n"
    "<b>Сеть</b>\n"
    "/wifi — сети поблизости\n"
    "/speedtest — скорость интернета\n"
    "/weather — погода"
)


@router.message(CommandStart())
@safe_handler
async def cmd_start(msg: Message, settings: Settings) -> None:
    await msg.answer(
        WELCOME,
        reply_markup=main_menu(weather_enabled=settings.weather_enabled),
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("help"))
@safe_handler
async def cmd_help(msg: Message) -> None:
    await msg.answer(HELP, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "menu:home")
@safe_handler
async def cb_home(cb: CallbackQuery, settings: Settings) -> None:
    if cb.message is not None:
        await cb.message.edit_text(
            WELCOME,
            reply_markup=main_menu(weather_enabled=settings.weather_enabled),
            parse_mode=ParseMode.HTML,
        )
    await cb.answer()


@router.callback_query(F.data == "menu:help")
@safe_handler
async def cb_help(cb: CallbackQuery) -> None:
    if cb.message is not None:
        await cb.message.edit_text(HELP, parse_mode=ParseMode.HTML)
    await cb.answer()


@router.callback_query(F.data == "noop")
@safe_handler
async def cb_noop(cb: CallbackQuery) -> None:
    await cb.answer()
