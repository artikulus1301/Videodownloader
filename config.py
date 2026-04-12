import os
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str
    DOWNLOAD_DIR: str = "/tmp/downloads"
    MAX_FILE_SIZE_MB: int = 50  # Telegram limit for bots without premium


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set!")
    return Config(BOT_TOKEN=token)


config = load_config()
