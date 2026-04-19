"""Модерновое окно настроек на CustomTkinter."""
from __future__ import annotations

import os
import webbrowser
from typing import Callable

import customtkinter as ctk
import pyperclip

from config import ENV_PATH, load_settings, save_settings


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SettingsApp(ctk.CTk):
    PADX = 24
    WIDTH = 520
    HEIGHT = 620

    def __init__(self, on_saved: Callable[[], None] | None = None) -> None:
        super().__init__()
        self.title("PC Control Bot — настройки")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.resizable(False, False)
        self._on_saved = on_saved
        self._build_ui()
        self._prefill_from_env()

    # ---------- UI building ----------
    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=self.PADX, pady=self.PADX)

        title = ctk.CTkLabel(
            container,
            text="PC Control Bot",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            container,
            text="Настройте токен и владельца, чтобы запустить бота.",
            text_color=("gray40", "gray70"),
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        self.token_entry = self._labeled_field(
            container,
            label="Telegram bot token",
            hint="Получить у @BotFather",
            with_paste=True,
            show="*",
        )

        self.owner_entry = self._labeled_field(
            container,
            label="Ваш Telegram ID",
            hint="Узнать ID: @userinfobot",
            with_paste=True,
        )

        ctk.CTkLabel(
            container,
            text="OpenWeather (опционально)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray80"),
        ).pack(anchor="w", pady=(14, 2))

        link = ctk.CTkLabel(
            container,
            text="openweathermap.org/api →",
            text_color=("#1f6feb", "#58a6ff"),
            cursor="hand2",
        )
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda _e: webbrowser.open("https://openweathermap.org/api"))

        self.weather_entry = self._labeled_field(
            container,
            label="API key",
            hint="",
            with_paste=True,
            show="*",
        )

        self.city_entry = self._labeled_field(
            container,
            label="Город (на английском)",
            hint="Пример: Moscow, London, Tokyo",
            with_paste=False,
        )

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 6))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            height=42,
            command=self._on_save_clicked,
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        save_close_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Сохранить и закрыть",
            height=42,
            fg_color=("#2fa666", "#2fa666"),
            hover_color=("#268a55", "#268a55"),
            command=self._on_save_close_clicked,
        )
        save_close_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.status = ctk.CTkLabel(container, text="", text_color=("gray30", "gray60"))
        self.status.pack(anchor="w", pady=(10, 0))

        file_note = ctk.CTkLabel(
            container,
            text=f"Файл настроек: {ENV_PATH.name} рядом с main.py",
            text_color=("gray50", "gray50"),
            font=ctk.CTkFont(size=11),
        )
        file_note.pack(anchor="w", pady=(2, 0))

    def _labeled_field(
        self,
        parent: ctk.CTkFrame,
        *,
        label: str,
        hint: str,
        with_paste: bool,
        show: str | None = None,
    ) -> ctk.CTkEntry:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w")

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", pady=(2, 0))

        entry = ctk.CTkEntry(row, height=36, show=show or "")
        entry.pack(side="left", fill="x", expand=True)

        if with_paste:
            btn = ctk.CTkButton(
                row,
                text="📋",
                width=42,
                height=36,
                command=lambda: self._paste_into(entry),
            )
            btn.pack(side="left", padx=(6, 0))

        if hint:
            ctk.CTkLabel(
                frame,
                text=hint,
                text_color=("gray50", "gray60"),
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w")

        return entry

    # ---------- Actions ----------
    def _paste_into(self, entry: ctk.CTkEntry) -> None:
        try:
            text = pyperclip.paste()
        except Exception:  # noqa: BLE001
            text = ""
        if text:
            entry.delete(0, "end")
            entry.insert(0, text.strip())

    def _prefill_from_env(self) -> None:
        current = load_settings()
        if current is None:
            # Возможно .env существует, но неполный — заполним то, что есть.
            if ENV_PATH.exists():
                from dotenv import dotenv_values

                raw = dotenv_values(ENV_PATH)
                self.token_entry.insert(0, raw.get("BOT_TOKEN", "") or "")
                self.owner_entry.insert(0, raw.get("OWNER_ID", "") or "")
                self.weather_entry.insert(0, raw.get("WEATHER_API_KEY", "") or "")
                self.city_entry.insert(0, raw.get("CITY", "") or "")
            return
        self.token_entry.insert(0, current.bot_token)
        self.owner_entry.insert(0, str(current.owner_id))
        self.weather_entry.insert(0, current.weather_api_key or "")
        self.city_entry.insert(0, current.city or "")

    def _on_save_clicked(self) -> None:
        if self._validate_and_save():
            self._set_status("Сохранено.", ok=True)

    def _on_save_close_clicked(self) -> None:
        if self._validate_and_save():
            if self._on_saved is not None:
                self._on_saved()
            self.after(400, self.destroy)

    def _validate_and_save(self) -> bool:
        token = self.token_entry.get().strip()
        owner_raw = self.owner_entry.get().strip()
        weather = self.weather_entry.get().strip()
        city = self.city_entry.get().strip()

        if not token or ":" not in token:
            self._set_status("Некорректный токен. Формат: 123456:AA...", ok=False)
            return False
        if not owner_raw.isdigit():
            self._set_status("Telegram ID должен быть числом.", ok=False)
            return False

        try:
            save_settings(token, int(owner_raw), weather, city)
        except OSError as exc:
            self._set_status(f"Ошибка записи .env: {exc}", ok=False)
            return False
        return True

    def _set_status(self, text: str, *, ok: bool) -> None:
        color = ("#1f8a4c", "#2fd17a") if ok else ("#b3261e", "#ff6b6b")
        self.status.configure(text=text, text_color=color)


def launch_settings_window() -> None:
    """Открывает окно настроек и ждёт его закрытия."""
    app = SettingsApp()
    app.mainloop()


if __name__ == "__main__":
    launch_settings_window()
