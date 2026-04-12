import os
import re
import uuid
import asyncio
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional

import yt_dlp

from config import config

logger = logging.getLogger(__name__)


class Platform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


@dataclass
class VideoInfo:
    title: str
    duration: Optional[int]  # seconds
    thumbnail: Optional[str]
    platform: Platform
    file_path: Optional[str] = None
    error: Optional[str] = None


def detect_platform(url: str) -> Platform:
    url = url.lower()
    if any(x in url for x in ["youtube.com", "youtu.be"]):
        return Platform.YOUTUBE
    if any(x in url for x in ["instagram.com", "instagr.am"]):
        return Platform.INSTAGRAM
    if any(x in url for x in ["tiktok.com", "vm.tiktok.com"]):
        return Platform.TIKTOK
    return Platform.UNKNOWN


def extract_url(text: str) -> Optional[str]:
    """Extract first URL from text."""
    pattern = r'https?://[^\s]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def _build_ydl_opts(output_path: str, platform: Platform) -> dict:
    """Build yt-dlp options based on platform."""
    base_opts = {
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    # Choose format: prefer mp4, max ~720p for size limits
    if platform == Platform.YOUTUBE:
        base_opts["format"] = (
            "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]"
            "/bestvideo[height<=720]+bestaudio"
            "/best[ext=mp4][height<=720]"
            "/best[height<=720]"
            "/best"
        )
        base_opts["merge_output_format"] = "mp4"
    elif platform == Platform.INSTAGRAM:
        base_opts["format"] = "best[ext=mp4]/best"
    elif platform == Platform.TIKTOK:
        base_opts["format"] = "best[ext=mp4]/best"
        # Some TikTok videos need a fake user agent
        base_opts["http_headers"] = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    return base_opts


async def get_video_info(url: str) -> VideoInfo:
    """Fetch video metadata without downloading."""
    platform = detect_platform(url)

    def _fetch():
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await asyncio.get_event_loop().run_in_executor(None, _fetch)
        return VideoInfo(
            title=info.get("title", "Unknown"),
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail"),
            platform=platform,
        )
    except Exception as e:
        logger.error(f"Failed to get info for {url}: {e}")
        return VideoInfo(
            title="Unknown",
            duration=None,
            thumbnail=None,
            platform=platform,
            error=str(e),
        )


async def download_video(url: str) -> VideoInfo:
    """Download video and return path to the file."""
    platform = detect_platform(url)
    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    output_template = os.path.join(config.DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    opts = _build_ydl_opts(output_template, platform)

    def _download():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Resolve actual filename
            filename = ydl.prepare_filename(info)
            # yt-dlp may change extension after merge
            if not os.path.exists(filename):
                # look for any file with our uuid prefix
                for f in os.listdir(config.DOWNLOAD_DIR):
                    if f.startswith(file_id):
                        filename = os.path.join(config.DOWNLOAD_DIR, f)
                        break
            return info, filename

    try:
        info, filename = await asyncio.get_event_loop().run_in_executor(None, _download)

        # Check file size
        if os.path.exists(filename):
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            if size_mb > config.MAX_FILE_SIZE_MB:
                os.remove(filename)
                return VideoInfo(
                    title=info.get("title", "Unknown"),
                    duration=info.get("duration"),
                    thumbnail=info.get("thumbnail"),
                    platform=platform,
                    error=f"❌ Файл слишком большой ({size_mb:.1f} МБ). Лимит — {config.MAX_FILE_SIZE_MB} МБ.",
                )

        return VideoInfo(
            title=info.get("title", "Unknown"),
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail"),
            platform=platform,
            file_path=filename,
        )

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        logger.error(f"DownloadError for {url}: {msg}")

        # Human-friendly error messages
        if "Private" in msg or "private" in msg:
            friendly = "❌ Видео является приватным и недоступно для скачивания."
        elif "age" in msg.lower():
            friendly = "❌ Видео ограничено по возрасту и недоступно без авторизации."
        elif "unavailable" in msg.lower() or "not available" in msg.lower():
            friendly = "❌ Видео недоступно (удалено или заблокировано)."
        elif "instagram" in msg.lower() and ("login" in msg.lower() or "auth" in msg.lower()):
            friendly = "❌ Instagram требует авторизации для этого видео. Публичные Reels скачиваются без проблем."
        else:
            friendly = f"❌ Не удалось скачать видео:\n<code>{msg[:200]}</code>"

        return VideoInfo(
            title="Unknown",
            duration=None,
            thumbnail=None,
            platform=platform,
            error=friendly,
        )
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        return VideoInfo(
            title="Unknown",
            duration=None,
            thumbnail=None,
            platform=platform,
            error=f"❌ Непредвиденная ошибка: {str(e)[:200]}",
        )


def cleanup_file(path: str):
    """Delete downloaded file after sending."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted temp file: {path}")
    except Exception as e:
        logger.warning(f"Could not delete {path}: {e}")
