# 🎬 Video Downloader Bot

Telegram-бот на **aiogram 3** для скачивания видео с YouTube, Instagram и TikTok.

## ✨ Возможности

- ▶️ **YouTube** — ролики, Shorts (до 720p)
- 📸 **Instagram** — публичные Reels и посты
- 🎵 **TikTok** — любые публичные видео
- Автоматическое определение платформы по ссылке
- Проверка размера файла (лимит Telegram — 50 МБ)
- Человекочитаемые сообщения об ошибках

---

## 🚀 Быстрый старт

### 1. Создай бота

1. Напиши [@BotFather](https://t.me/BotFather) в Telegram
2. `/newbot` → задай имя и username
3. Скопируй токен

### 2. Клонируй / скачай проект

```bash
git clone <your-repo>
cd video_downloader_bot
```

### 3. Установка зависимостей

#### Вариант A — локально (нужен Python 3.10+)

```bash
# Установи ffmpeg (нужен для YouTube)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# Установи Python-зависимости
pip install -r requirements.txt

# Создай .env файл
echo "BOT_TOKEN=ваш_токен_здесь" > .env

# Запусти
BOT_TOKEN=ваш_токен_здесь python bot.py
```

#### Вариант B — Docker (рекомендуется)

```bash
# Создай файл .env
echo "BOT_TOKEN=ваш_токен_здесь" > .env

# Запусти
docker-compose up -d

# Логи
docker-compose logs -f
```

---

## 📁 Структура проекта

```
video_downloader_bot/
├── bot.py          # Точка входа, инициализация бота
├── config.py       # Конфигурация (токен, лимиты)
├── handlers.py     # Обработчики сообщений
├── downloader.py   # Логика скачивания (yt-dlp)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Настройки (config.py)

| Параметр | По умолчанию | Описание |
|---|---|---|
| `BOT_TOKEN` | — | Токен бота (обязательно) |
| `DOWNLOAD_DIR` | `downloads` | Папка для временных файлов |
| `MAX_FILE_SIZE_MB` | `50` | Лимит размера видео |

---

## ⚠️ Ограничения

- **50 МБ** — лимит Telegram для обычных ботов
- **Instagram** — работает только с публичными аккаунтами
- **YouTube** — видео с возрастным ограничением без cookie не скачать
- **TikTok** — очень редко меняет защиту, yt-dlp обычно справляется

---

## 🍪 YouTube с авторизацией (возрастные ограничения)

Если нужны видео с возрастными ограничениями, добавь cookies в `downloader.py`:

```python
base_opts["cookiefile"] = "cookies.txt"  # экспорт из браузера
```

Экспортировать cookies можно расширением [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc).

---

## 📦 Зависимости

- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — скачивание видео
- [ffmpeg](https://ffmpeg.org/) — объединение видео и аудио (YouTube)
