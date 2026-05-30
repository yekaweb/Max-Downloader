"""
DLBot Configuration Module
Uses Pydantic v2 for type-safe settings management
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import os


class DatabaseSettings(BaseSettings):
    """Database configuration - supports both PostgreSQL and SQLite"""
    db_type: str = Field("sqlite", description="Database type (sqlite or postgresql)")
    host: str = Field("localhost", description="PostgreSQL host")
    port: int = Field(5432, description="PostgreSQL port")
    user: str = Field("dlbot_user", description="Database user")
    password: str = Field("secure_password_here", description="Database password")
    name: str = Field("dlbot_db", description="Database name")
    path: str = Field("./dlbot.db", description="SQLite database path")
    pool_size: int = Field(20, description="Connection pool size")
    max_overflow: int = Field(10, description="Max overflow connections")
    
    @property
    def dsn(self) -> str:
        """Generate appropriate DSN based on database type"""
        if self.db_type.lower() == "sqlite":
            return f"sqlite+aiosqlite:///{self.path}"
        else:
            return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False


class RedisSettings(BaseSettings):
    """Redis configuration"""
    host: str = Field("localhost", description="Redis host")
    port: int = Field(6379, description="Redis port")
    db: int = Field(0, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")
    decode_responses: bool = Field(True, description="Decode responses to strings")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    session_ttl: int = Field(86400, description="Session TTL in seconds")
    
    @property
    def url(self) -> str:
        """Generate Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False


class TelegramBotSettings(BaseSettings):
    """Telegram Bot configuration"""
    token: str = Field(default="", description="Telegram Bot API token")
    admin_ids: List[int] = Field(default_factory=list, description="Admin user IDs")
    username: str = Field("dlbot", description="Bot username")
    
    @validator("admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v or []
    
    class Config:
        env_prefix = "BOT_"
        case_sensitive = False


class PyrogramSettings(BaseSettings):
    """Pyrogram configuration for large file uploads"""
    app_id: int = Field(..., description="Telegram App ID")
    app_hash: str = Field(..., description="Telegram App Hash")
    session_name: str = Field("dlbot_session", description="Session name")
    
    class Config:
        env_prefix = "PYROGRAM_"
        case_sensitive = False


class CelerySettings(BaseSettings):
    """Celery task queue configuration"""
    broker_url: str = Field("redis://localhost:6379/0", description="Celery broker URL")
    result_backend: str = Field("redis://localhost:6379/1", description="Celery result backend")
    task_time_limit: int = Field(3600, description="Task time limit in seconds")
    
    class Config:
        env_prefix = "CELERY_"
        case_sensitive = False


class PaymentSettings(BaseSettings):
    """Payment gateway configuration"""
    cryptobot_api_token: Optional[str] = Field(None, description="CryptoBot API token")
    zarinpal_merchant_id: Optional[str] = Field(None, description="ZarinPal Merchant ID")
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class FileStorageSettings(BaseSettings):
    """File storage configuration"""
    temp_download_dir: str = Field("./temp_downloads", description="Temporary download directory")
    cache_file_dir: str = Field("./cached_files", description="Cached files directory")
    max_file_size: int = Field(4294967296, description="Max file size in bytes (4GB)")
    max_file_age_hours: int = Field(48, description="Max file age in hours")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create directories if they don't exist
        Path(self.temp_download_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_file_dir).mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class LocalizationSettings(BaseSettings):
    """Localization configuration"""
    default_language: str = Field("fa", description="Default language")
    supported_languages: List[str] = Field(default=["fa", "en", "ar", "ru", "zh"], description="Supported languages")
    
    @validator("supported_languages", pre=True)
    def parse_languages(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        if not v:
            return ["fa", "en", "ar", "ru", "zh"]
        return v
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class FeatureFlags(BaseSettings):
    """Feature flag configuration"""
    enable_referral_system: bool = Field(True, description="Enable referral system")
    enable_force_join: bool = Field(True, description="Enable force-join middleware")
    enable_broadcast: bool = Field(True, description="Enable broadcast system")
    enable_admin_panel: bool = Field(True, description="Enable admin panel")
    
    class Config:
        env_prefix = "ENABLE_"
        case_sensitive = False


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    level: str = Field("INFO", description="Log level")
    file: str = Field("./logs/dlbot.log", description="Log file path")
    format: str = Field("json", description="Log format")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create log directory if it doesn't exist
        Path(self.file).parent.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_prefix = "LOG_"
        case_sensitive = False


class WebPanelSettings(BaseSettings):
    """FastAPI Web Admin Panel configuration"""
    host: str = Field("0.0.0.0", description="Web server host")
    port: int = Field(8000, description="Web server port")
    reload: bool = Field(True, description="Auto-reload on code changes")
    jwt_secret_key: str = Field("your_super_secret_key_change_in_production", description="JWT secret key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(24, description="JWT token expiration in hours")
    
    class Config:
        env_prefix = "WEB_"
        case_sensitive = False


class AppSettings(BaseSettings):
    """Main application settings"""
    env: str = Field("development", description="Environment (development/production)")
    version: str = Field("1.0.0", description="App version")
    debug: bool = Field(True, description="Debug mode")
    worker_count: int = Field(4, description="Number of worker processes")
    
    # Nested settings - use Field default_factory to load from environment
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    telegram: TelegramBotSettings = Field(default_factory=TelegramBotSettings)
    pyrogram: Optional[PyrogramSettings] = Field(default_factory=lambda: PyrogramSettings() if all([os.getenv("PYROGRAM_APP_ID"), os.getenv("PYROGRAM_APP_HASH")]) else None)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    payment: PaymentSettings = Field(default_factory=PaymentSettings)
    file_storage: FileStorageSettings = Field(default_factory=FileStorageSettings)
    localization: LocalizationSettings = Field(default_factory=LocalizationSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    web_panel: WebPanelSettings = Field(default_factory=WebPanelSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        nested_delimiter = "__"
        extra = "allow"


# Global settings instance
def load_settings() -> AppSettings:
    """Load and validate settings from environment"""
    return AppSettings()


# Create singleton instance
settings = load_settings()

__all__ = ["settings", "AppSettings", "load_settings"]
