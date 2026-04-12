import logging
import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, URLInputFile
from aiogram.utils.chat_action import ChatActionSender

from downloader import (
    detect_platform,
    extract_url,
    download_video,
    cleanup_file,
    Platform,
)

logger = logging.getLogger(__name__)
router = Router()

PLATFORM_EMOJI = {
    Platform.YOUTUBE: "▶️ YouTube",
    Platform.INSTAGRAM: "📸 Instagram",
    Platform.TIKTOK: "🎵 TikTok",
    Platform.UNKNOWN: "🌐 Unknown",
}


# ─── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Привет! Я бот для скачивания видео.</b>\n\n"
        "Поддерживаемые платформы:\n"
        "  ▶️ <b>YouTube</b> — ролики и Shorts\n"
        "  📸 <b>Instagram</b> — Reels и посты\n"
        "  🎵 <b>TikTok</b> — любые видео\n\n"
        "Просто отправь мне ссылку — и я пришлю видео! 🚀\n\n"
        "<i>Лимит: до 50 МБ (ограничение Telegram для ботов)</i>"
    )


# ─── /help ─────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
        "1. Скопируй ссылку на видео\n"
        "2. Отправь её в этот чат\n"
        "3. Подожди — бот пришлёт тебе видео\n\n"
        "<b>Примеры ссылок:</b>\n"
        "• <code>https://youtu.be/dQw4w9WgXcQ</code>\n"
        "• <code>https://www.instagram.com/reel/...</code>\n"
        "• <code>https://www.tiktok.com/@user/video/...</code>\n\n"
        "<b>Ограничения:</b>\n"
        "• Максимальный размер файла — <b>50 МБ</b>\n"
        "• Приватные видео скачать нельзя\n"
        "• Видео с возрастным ограничением могут не работать\n\n"
        "По вопросам — /start"
    )


# ─── URL handler ───────────────────────────────────────────────────────────────

@router.message(F.text)
async def handle_url(message: Message):
    url = extract_url(message.text)

    if not url:
        await message.answer(
            "🔗 Отправь мне ссылку на видео с YouTube, Instagram или TikTok.\n"
            "Используй /help если нужна помощь."
        )
        return

    platform = detect_platform(url)
    if platform == Platform.UNKNOWN:
        await message.answer(
            "⚠️ Эта ссылка не поддерживается.\n\n"
            "Я умею скачивать видео с:\n"
            "  ▶️ YouTube\n"
            "  📸 Instagram\n"
            "  🎵 TikTok"
        )
        return

    status_msg = await message.answer(
        f"⏳ Скачиваю видео с {PLATFORM_EMOJI[platform]}…\n"
        "<i>Это может занять несколько секунд</i>"
    )

    try:
        async with ChatActionSender.upload_video(bot=message.bot, chat_id=message.chat.id):
            result = await download_video(url)

        if result.error:
            await status_msg.edit_text(result.error)
            return

        if not result.file_path or not os.path.exists(result.file_path):
            await status_msg.edit_text("❌ Файл не найден после скачивания. Попробуй ещё раз.")
            return

        # Format duration
        duration_text = ""
        if result.duration:
            mins, secs = divmod(result.duration, 60)
            hours, mins = divmod(mins, 60)
            if hours:
                duration_text = f"⏱ {hours}:{mins:02d}:{secs:02d}"
            else:
                duration_text = f"⏱ {mins}:{secs:02d}"

        caption = (
            f"{PLATFORM_EMOJI[platform]}\n"
            f"📹 <b>{result.title[:200]}</b>\n"
            f"{duration_text}"
        ).strip()

        video_file = FSInputFile(result.file_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            supports_streaming=True,
        )
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error in handle_url: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Произошла ошибка при отправке видео.\n"
            f"<code>{str(e)[:200]}</code>"
        )
    finally:
        if result and result.file_path:
            cleanup_file(result.file_path)
