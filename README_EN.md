# PC Control Bot

> [Русская версия](README.md)

Telegram bot for remote Windows PC control. Hardware stats, processes, screenshots, power management, cursor, clipboard — all from chat.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.15-2CA5E0)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Hardware**: CPU, RAM, GPU (Nvidia), disks, temperature, load
- **Power**: lock screen, sleep, hibernate, restart, shutdown, timers
- **Processes**: task list, kill by name, launch `.exe`, mass close
- **Media**: screenshots of all monitors, brightness control
- **Clipboard**: get / set text, auto-send images from URL
- **Network**: Wi-Fi list, speedtest, weather via OpenWeather
- **Cursor**: remote mouse control & clicks via inline buttons
- **GUI settings**: modern CustomTkinter window for initial setup

## Security

- Bot responds **only** to the owner — all other messages are ignored
- `OWNER_ID` is checked at middleware level before any handlers
- Secrets are stored in `.env`, excluded from git
- Remote shell commands are intentionally absent

## Stack

- [`aiogram 3`](https://docs.aiogram.dev/) — async Telegram bot
- [`CustomTkinter`](https://customtkinter.tomschimansky.com/) — modern GUI
- `psutil`, `pywin32`, `mss`, `pyautogui`, `screen-brightness-control`
- `aiohttp` — async HTTP requests to OpenWeather

## Installation

```bash
git clone https://github.com/Th3Nekit/pc-control-telegram.git
cd pc-control-telegram
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather), copy the token
2. Get your Telegram ID from [@userinfobot](https://t.me/userinfobot)
3. (optional) Register at [openweathermap.org](https://openweathermap.org/api) for `/weather`
4. Run setup:

```bash
python main.py --setup
```

A window will open — paste token, ID and weather key, click "Save". Data goes to `.env` next to `main.py`.

Or manually: copy `.env.example` to `.env` and fill it in.

## Running

```bash
python main.py
```

First launch without `.env` will automatically open the setup window.

## Commands

| Command | Description |
|---|---|
| `/start`, `/help` | Main menu and help |
| `/checkpc` | PC specs |
| `/performance` | Current load |
| `/disks` | Disk status |
| `/screenshot` | Screenshots of all monitors |
| `/lock` | Lock screen |
| `/power` | Power menu (sleep, restart, shutdown, hibernate, timer) |
| `/tasks` | Process list |
| `/killall` | Close all user processes |
| `/open <exe>` | Launch a program |
| `/close <name>` | Close process by name |
| `/clip` | Get clipboard contents |
| `/setclip <text>` | Write to clipboard |
| `/brightness <0-100>` | Screen brightness |
| `/wifi` | Available Wi-Fi networks |
| `/speedtest` | Internet speed |
| `/weather` | Weather in specified city |
| `/control` | Cursor control |

## Structure

```
pc-control-bot/
├── main.py              # Entry point, mode selection (bot / setup)
├── gui.py               # Settings window (CustomTkinter)
├── config.py            # Loading and saving .env
├── security.py          # OWNER_ID check middleware
├── keyboards.py         # Inline and reply keyboards
├── utils.py             # Helpers, error decorators, run_sync
└── handlers/
    ├── start.py
    ├── system.py
    ├── power.py
    ├── tasks.py
    ├── screen.py
    ├── clipboard.py
    ├── network.py
    ├── weather.py
    └── control.py
```

## Build to `.exe`

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name PcControlBot main.py
```

The `.exe` will appear in `dist/`. Place `.env` next to it.

## Limitations

- Windows only (`win32api`, `winshell`, `nvidia-smi`)
- GPU stats available only for Nvidia
- Internet speed measured via free `speedtest-cli`, may take 30+ seconds

## License

MIT © 2026 Th3Nekit
