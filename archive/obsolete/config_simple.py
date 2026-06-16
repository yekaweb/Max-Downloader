"""
Minimal Configuration for Testing
Pure Python - No Pydantic!
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """Simplified settings class - NO Pydantic validation"""
    
    def __init__(self):
        # Telegram
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.ADMIN_IDS = os.getenv("ADMIN_IDS", "")
        self.BOT_USERNAME = os.getenv("BOT_USERNAME", "dlbot")
        
        # Parse admin IDs
        if self.ADMIN_IDS and isinstance(self.ADMIN_IDS, str):
            self.ADMIN_IDS_LIST = [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]
        else:
            self.ADMIN_IDS_LIST = []
        
        # Database
        self.DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
        self.DB_PATH = os.getenv("DB_PATH", "./dlbot.db")
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_USER = os.getenv("DB_USER", "dlbot_user")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
        self.DB_NAME = os.getenv("DB_NAME", "dlbot_db")
        
        # Pyrogram
        self.PYROGRAM_APP_ID = os.getenv("PYROGRAM_APP_ID", "")
        self.PYROGRAM_APP_HASH = os.getenv("PYROGRAM_APP_HASH", "")
        self.PYROGRAM_SESSION_NAME = os.getenv("PYROGRAM_SESSION_NAME", "dlbot_session")
        
        # Redis
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
        
        # Localization - SIMPLE parsing (no validation)
        default_langs = "fa,en,ar,ru,zh"
        supported_str = os.getenv("SUPPORTED_LANGUAGES", default_langs)
        self.DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fa")
        
        # Parse languages safely
        try:
            if supported_str and isinstance(supported_str, str):
                self.SUPPORTED_LANGUAGES = [x.strip() for x in supported_str.split(",") if x.strip()]
            else:
                self.SUPPORTED_LANGUAGES = default_langs.split(",")
        except:
            self.SUPPORTED_LANGUAGES = default_langs.split(",")
        
        # Storage
        self.TEMP_DOWNLOAD_DIR = Path(os.getenv("TEMP_DOWNLOAD_DIR", "./temp_downloads"))
        self.CACHE_FILE_DIR = Path(os.getenv("CACHE_FILE_DIR", "./cached_files"))
        self.LOG_FILE = Path(os.getenv("LOG_FILE", "./logs/dlbot.log"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Features
        self.ENABLE_REFERRAL_SYSTEM = os.getenv("ENABLE_REFERRAL_SYSTEM", "true").lower() == "true"
        self.ENABLE_FORCE_JOIN = os.getenv("ENABLE_FORCE_JOIN", "true").lower() == "true"
        self.ENABLE_BROADCAST = os.getenv("ENABLE_BROADCAST", "true").lower() == "true"
        self.ENABLE_ADMIN_PANEL = os.getenv("ENABLE_ADMIN_PANEL", "true").lower() == "true"
        
        # App
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # Web Panel
        self.WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
        self.WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
        
        # Create directories
        self.TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_FILE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    @property
    def database_url(self):
        """Get database URL for SQLAlchemy (sync for Alembic)"""
        if self.DB_TYPE == "sqlite":
            # Normalize path
            path = self.DB_PATH.replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return f"sqlite:///{path}"
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_async_url(self):
        """Get async database URL for runtime"""
        if self.DB_TYPE == "sqlite":
            # Normalize path
            path = self.DB_PATH.replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return f"sqlite+aiosqlite:///{path}"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self):
        """Get Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

# Create singleton instance
settings = Settings()

