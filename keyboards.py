"""Inline-клавиатуры для модернового UI."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(weather_enabled: bool = True) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💻 Характеристики", callback_data="menu:checkpc")
    b.button(text="📊 Нагрузка", callback_data="menu:performance")
    b.button(text="💽 Диски", callback_data="menu:disks")
    b.button(text="📷 Скриншот", callback_data="menu:screenshot")
    b.button(text="🔒 Блокировка", callback_data="menu:lock")
    b.button(text="⚡ Питание", callback_data="menu:power")
    b.button(text="📝 Процессы", callback_data="menu:tasks")
    b.button(text="📋 Буфер", callback_data="menu:clipboard")
    b.button(text="🌐 Wi-Fi", callback_data="menu:wifi")
    b.button(text="🚀 Speedtest", callback_data="menu:speedtest")
    b.button(text="🖱 Курсор", callback_data="menu:control")
    b.button(text="☀️ Яркость", callback_data="menu:brightness")
    if weather_enabled:
        b.button(text="🌤 Погода", callback_data="menu:weather")
    b.button(text="ℹ️ Помощь", callback_data="menu:help")
    b.adjust(2)
    return b.as_markup()


def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Меню", callback_data="menu:home")]
        ]
    )


def power_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💤 Сон", callback_data="power:sleep")
    b.button(text="❄️ Гибернация", callback_data="power:hibernate")
    b.button(text="🔁 Перезагрузка", callback_data="power:restart")
    b.button(text="⛔ Выключить", callback_data="power:shutdown")
    b.button(text="⏱ 10 мин", callback_data="power:timer:10")
    b.button(text="⏱ 30 мин", callback_data="power:timer:30")
    b.button(text="⏱ 60 мин", callback_data="power:timer:60")
    b.button(text="✖️ Отменить таймер", callback_data="power:cancel")
    b.button(text="↩️ Меню", callback_data="menu:home")
    b.adjust(2)
    return b.as_markup()


def control_pad() -> InlineKeyboardMarkup:
    """Игровая D-Pad раскладка для управления курсором."""
    nop = InlineKeyboardButton(text=" ", callback_data="noop")
    rows = [
        [
            nop,
            InlineKeyboardButton(text="⬆️", callback_data="ctl:up"),
            nop,
        ],
        [
            InlineKeyboardButton(text="⬅️", callback_data="ctl:left"),
            InlineKeyboardButton(text="🖱", callback_data="ctl:click"),
            InlineKeyboardButton(text="➡️", callback_data="ctl:right"),
        ],
        [
            InlineKeyboardButton(text="🖱🖱", callback_data="ctl:double"),
            InlineKeyboardButton(text="⬇️", callback_data="ctl:down"),
            InlineKeyboardButton(text="🖱R", callback_data="ctl:rclick"),
        ],
        [
            InlineKeyboardButton(text="Шаг ×5", callback_data="ctl:step:5"),
            InlineKeyboardButton(text="Шаг ×25", callback_data="ctl:step:25"),
            InlineKeyboardButton(text="Шаг ×100", callback_data="ctl:step:100"),
        ],
        [InlineKeyboardButton(text="↩️ Меню", callback_data="menu:home")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def brightness_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for value in (10, 25, 50, 75, 100):
        b.button(text=f"{value}%", callback_data=f"br:{value}")
    b.button(text="↩️ Меню", callback_data="menu:home")
    b.adjust(3)
    return b.as_markup()
