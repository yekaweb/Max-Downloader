"""Application settings with strong validation using Pydantic v2."""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

load_dotenv()


def _parse_int_list(value: Optional[str | List[int]]) -> List[int]:
    if value is None:
        return []
    if isinstance(value, list):
        return [int(item) for item in value if item is not None]
    if isinstance(value, str):
        return [int(item.strip()) for item in value.split(",") if item.strip()]
    raise ValueError("ADMIN_IDS must be a comma-separated string or list of integers")


def _parse_str_list(value: Optional[str | List[str]]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    raise ValueError("SUPPORTED_LANGUAGES must be a comma-separated string or list of strings")


def _parse_bool(value: Optional[str | bool | int]) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    ADMIN_IDS: str = Field("", env="ADMIN_IDS")
    BOT_USERNAME: str = Field("dlbot", env="BOT_USERNAME")

    # Database
    DB_TYPE: str = Field("sqlite", env="DB_TYPE")
    DB_PATH: Path = Field(Path("./dlbot.db"), env="DB_PATH")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DB_USER: str = Field("dlbot_user", env="DB_USER")
    DB_PASSWORD: str = Field("password", env="DB_PASSWORD")
    DB_NAME: str = Field("dlbot_db", env="DB_NAME")

    # Pyrogram
    PYROGRAM_APP_ID: Optional[int] = Field(None, env="PYROGRAM_APP_ID")
    PYROGRAM_APP_HASH: Optional[str] = Field(None, env="PYROGRAM_APP_HASH")
    PYROGRAM_SESSION_NAME: str = Field("dlbot_session", env="PYROGRAM_SESSION_NAME")

    # Redis
    REDIS_ENABLED: bool = Field(True, env="REDIS_ENABLED")
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")

    # Localization
    SUPPORTED_LANGUAGES_RAW: str = Field("", env="SUPPORTED_LANGUAGES")
    DEFAULT_LANGUAGE: str = Field("fa", env="DEFAULT_LANGUAGE")

    # Storage
    TEMP_DOWNLOAD_DIR: Path = Field(Path("./temp_downloads"), env="TEMP_DOWNLOAD_DIR")
    CACHE_FILE_DIR: Path = Field(Path("./cached_files"), env="CACHE_FILE_DIR")
    LOG_FILE: Path = Field(Path("./logs/dlbot.log"), env="LOG_FILE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # Features
    ENABLE_REFERRAL_SYSTEM: bool = Field(True, env="ENABLE_REFERRAL_SYSTEM")
    ENABLE_FORCE_JOIN: bool = Field(True, env="ENABLE_FORCE_JOIN")
    ENABLE_BROADCAST: bool = Field(True, env="ENABLE_BROADCAST")
    ENABLE_ADMIN_PANEL: bool = Field(True, env="ENABLE_ADMIN_PANEL")

    # App
    APP_ENV: str = Field("development", env="APP_ENV")
    APP_VERSION: str = Field("1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(True, env="DEBUG")

    # Web Panel
    WEB_HOST: str = Field("0.0.0.0", env="WEB_HOST")
    WEB_PORT: int = Field(8000, env="WEB_PORT")

    # Payments
    CRYPTOPAY_TOKEN: str = Field("", env="CRYPTOPAY_TOKEN")
    ZARINPAL_MERCHANT: str = Field("", env="ZARINPAL_MERCHANT")
    NOWPAYMENTS_KEY: str = Field("", env="NOWPAYMENTS_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False,
    }

    @property
    def SUPPORTED_LANGUAGES(self) -> List[str]:
        return _parse_str_list(self.SUPPORTED_LANGUAGES_RAW)

    @field_validator("REDIS_ENABLED", mode="before")
    @classmethod
    def _validate_bool_flags(cls, value):
        return _parse_bool(value)

    @field_validator("DB_PATH", mode="before")
    @classmethod
    def _normalize_paths(cls, value):
        if isinstance(value, str):
            return Path(value)
        return value

    def __init__(self, **values):
        super().__init__(**values)
        self.TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_FILE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    @property
    def ADMIN_IDS_LIST(self) -> List[int]:
        return _parse_int_list(self.ADMIN_IDS)

    @property
    def database_url(self) -> str:
        if self.DB_TYPE.lower() == "sqlite":
            return f"sqlite:///{self.DB_PATH.as_posix()}"
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_async_url(self) -> str:
        if self.DB_TYPE.lower() == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_PATH.as_posix()}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
