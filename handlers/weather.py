"""Погода через OpenWeather API (асинхронно)."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import aiohttp
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import Settings
from keyboards import back_to_menu
from utils import safe_handler

router = Router(name="weather")

WEATHER_MAP = {
    "Clear": "Ясно",
    "Clouds": "Облачно",
    "Drizzle": "Морось",
    "Rain": "Дождь",
    "Thunderstorm": "Гроза",
    "Snow": "Снег",
    "Mist": "Туман",
    "Fog": "Туман",
    "Smoke": "Дым",
    "Haze": "Мгла",
    "Dust": "Пыль",
}


async def _fetch_weather(api_key: str, city: str) -> dict | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "ru"}
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


def _format_weather(data: dict, city: str) -> str:
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather = (data.get("weather") or [{}])[0]
    sys = data.get("sys", {})
    tz_offset = int(data.get("timezone", 0))

    desc_key = weather.get("main", "")
    description = WEATHER_MAP.get(desc_key) or (weather.get("description") or "—").capitalize()

    def fmt_time(ts: int | None) -> str:
        if not ts:
            return "—"
        tz = timezone(timedelta(seconds=tz_offset))
        return datetime.fromtimestamp(ts, tz=tz).strftime("%H:%M")

    temp = main.get("temp")
    feels = main.get("feels_like")
    pressure_hpa = main.get("pressure", 0)
    pressure_mmhg = round(pressure_hpa * 0.7500617, 1)

    return (
        f"<b>🌤 Погода — {city}</b>\n\n"
        f"<b>{description}</b>, {temp:.0f}°C (ощущается {feels:.0f}°C)\n\n"
        f"💦 Влажность: {main.get('humidity', '—')}%\n"
        f"💨 Ветер: {wind.get('speed', '—')} м/с\n"
        f"🌡 Давление: {pressure_mmhg} мм рт. ст.\n"
        f"🌅 Восход: {fmt_time(sys.get('sunrise'))}\n"
        f"🌇 Закат:  {fmt_time(sys.get('sunset'))}"
    )


@router.message(Command("weather"))
@router.callback_query(F.data == "menu:weather")
@safe_handler
async def cmd_weather(event: Message | CallbackQuery, settings: Settings) -> None:
    target = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer()

    if target is None:
        return

    if not settings.weather_enabled:
        await target.answer(
            "⚠️ Погода не настроена. Заполните <code>WEATHER_API_KEY</code> "
            "и <code>CITY</code> в <b>.env</b>.",
            reply_markup=back_to_menu(),
            parse_mode=ParseMode.HTML,
        )
        return

    data = await _fetch_weather(settings.weather_api_key or "", settings.city or "")
    if not data:
        await target.answer(
            "⚠️ Не удалось получить погоду. Проверьте ключ и название города.",
            reply_markup=back_to_menu(),
        )
        return

    await target.answer(
        _format_weather(data, settings.city or ""),
        reply_markup=back_to_menu(),
        parse_mode=ParseMode.HTML,
    )
