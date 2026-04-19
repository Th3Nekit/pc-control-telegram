# PC Control Bot

Telegram-бот для удалённого управления Windows-компьютером. Характеристики, процессы, скриншоты, управление питанием, курсором, буфером обмена — всё прямо из чата.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.15-2CA5E0)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Возможности

- **Железо**: процессор, ОЗУ, GPU (Nvidia), диски, температура, нагрузка
- **Питание**: блокировка экрана, сон, гибернация, перезагрузка, выключение, таймеры
- **Процессы**: список задач, kill по имени, запуск `.exe`, массовое закрытие
- **Медиа**: скриншоты всех мониторов, управление яркостью
- **Буфер обмена**: получить / установить текст, автоотправка картинок из URL
- **Сеть**: список Wi-Fi сетей, speedtest, погода через OpenWeather
- **Курсор**: удалённое управление мышью и кликами через inline-кнопки
- **GUI-настройки**: современное окно на CustomTkinter для первичной настройки

## Безопасность

- Бот отвечает **только** владельцу — все остальные сообщения игнорируются
- `OWNER_ID` проверяется на уровне middleware до любых хэндлеров
- Секреты хранятся в `.env`, который исключён из git
- Команды удалённого шелла намеренно отсутствуют

## Стек

- [`aiogram 3`](https://docs.aiogram.dev/) — асинхронный Telegram-бот
- [`CustomTkinter`](https://customtkinter.tomschimansky.com/) — современный GUI
- `psutil`, `pywin32`, `mss`, `pyautogui`, `screen-brightness-control`
- `aiohttp` — асинхронные HTTP-запросы к OpenWeather

## Установка

```bash
git clone https://github.com/<yourname>/pc-control-bot.git
cd pc-control-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

1. Создайте бота через [@BotFather](https://t.me/BotFather), скопируйте токен
2. Узнайте свой Telegram ID у [@userinfobot](https://t.me/userinfobot)
3. (опционально) Зарегистрируйтесь на [openweathermap.org](https://openweathermap.org/api) ради `/weather`
4. Запустите настройку:

```bash
python main.py --setup
```

Откроется окно, вставьте токен, ID и ключ погоды, нажмите «Сохранить». Данные лягут в `.env` рядом с `main.py`.

Или вручную: скопируйте `.env.example` в `.env` и заполните.

## Запуск

```bash
python main.py
```

Первый запуск без `.env` автоматически откроет окно настроек.

## Команды

| Команда | Описание |
|---|---|
| `/start`, `/help` | Главное меню и справка |
| `/checkpc` | Характеристики ПК |
| `/performance` | Текущая нагрузка |
| `/disks` | Статус дисков |
| `/screenshot` | Скриншоты всех мониторов |
| `/lock` | Заблокировать экран |
| `/power` | Меню питания (sleep, restart, shutdown, hibernate, timer) |
| `/tasks` | Список процессов |
| `/killall` | Закрыть все пользовательские процессы |
| `/open <exe>` | Запустить программу |
| `/close <name>` | Закрыть процесс по имени |
| `/clip` | Получить содержимое буфера обмена |
| `/setclip <text>` | Записать в буфер обмена |
| `/brightness <0-100>` | Яркость экрана |
| `/wifi` | Список доступных Wi-Fi сетей |
| `/speedtest` | Скорость интернета |
| `/weather` | Погода в указанном городе |
| `/control` | Управление курсором |

## Структура

```
pc-control-bot/
├── main.py              # Точка входа, выбор режима (bot / setup)
├── gui.py               # Окно настроек на CustomTkinter
├── config.py            # Загрузка и сохранение .env
├── security.py          # Middleware проверки OWNER_ID
├── keyboards.py         # Inline и reply клавиатуры
├── utils.py             # Хелперы, декораторы ошибок, run_sync
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

## Сборка в `.exe`

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name PcControlBot main.py
```

Готовый `.exe` появится в `dist/`. `.env` положите рядом.

## Ограничения

- Только Windows (используются `win32api`, `winshell`, `nvidia-smi`)
- GPU-статистика доступна только для Nvidia
- Скорость интернета измеряется через бесплатный `speedtest-cli`, может занимать 30+ секунд

## Лицензия

MIT © 2026 TheNekit
