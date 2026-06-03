"""
Example configuration file.
Copy this file to config.py and replace placeholder values with your own secrets.
Do NOT commit real secret values to GitHub.
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional

class DatabaseSettings(BaseSettings):
    db_type: str = Field("sqlite", description="Database type (sqlite or postgresql)")
    host: str = Field("localhost", description="PostgreSQL host")
    port: int = Field(5432, description="PostgreSQL port")
    user: str = Field("dlbot_user", description="Database user")
    password: str = Field("YOUR_DB_PASSWORD", description="Database password")
    name: str = Field("dlbot_db", description="Database name")
    path: str = Field("./dlbot.db", description="SQLite database path")

    class Config:
        env_prefix = "DB_"
        case_sensitive = False

class RedisSettings(BaseSettings):
    host: str = Field("localhost", description="Redis host")
    port: int = Field(6379, description="Redis port")
    db: int = Field(0, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")

    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False

class TelegramBotSettings(BaseSettings):
    token: str = Field("", description="Telegram Bot API token")
    admin_ids: List[int] = Field(default_factory=list, description="Admin user IDs")

    class Config:
        env_prefix = "BOT_"
        case_sensitive = False

class PyrogramSettings(BaseSettings):
    app_id: int = Field(0, description="Telegram App ID")
    app_hash: str = Field("YOUR_PYROGRAM_APP_HASH", description="Telegram App Hash")

    class Config:
        env_prefix = "PYROGRAM_"
        case_sensitive = False

class WebPanelSettings(BaseSettings):
    jwt_secret_key: str = Field("YOUR_JWT_SECRET_KEY", description="JWT secret key")

    class Config:
        env_prefix = "WEB_"
        case_sensitive = False

class AppSettings(BaseSettings):
    env: str = Field("development", description="Environment")
    debug: bool = Field(True, description="Debug mode")

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    telegram: TelegramBotSettings = Field(default_factory=TelegramBotSettings)
    pyrogram: Optional[PyrogramSettings] = Field(default_factory=PyrogramSettings)
    web_panel: WebPanelSettings = Field(default_factory=WebPanelSettings)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
