"""Localization module for DLBot"""

import json
from pathlib import Path

class Localization:
    """ماژول ترجمه"""
    
    def __init__(self):
        self.locales = {}
        self.default_lang = "fa"
        self._load_locales()
    
    def _load_locales(self):
        """بارگذاری فایل‌های localization"""
        locales_dir = Path(__file__).parent
        
        for lang_file in locales_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.locales[lang_code] = json.load(f)
            except Exception as e:
                print(f"❌ خطا در بارگذاری {lang_code}: {e}")
    
    def get(self, key: str, lang: str = "fa", default: str = "") -> str:
        """دریافت ترجمه
        
        مثال:
        - get("start.title", "fa")
        - get("download.error", "en")
        """
        if lang not in self.locales:
            lang = self.default_lang
        
        keys = key.split(".")
        value = self.locales[lang]
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value if isinstance(value, str) else default
    
    def get_dict(self, section: str, lang: str = "fa") -> dict:
        """دریافت یک بخش کامل"""
        if lang not in self.locales:
            lang = self.default_lang
        
        return self.locales[lang].get(section, {})


# نمونه جهانی
i18n = Localization()

__all__ = ["i18n", "Localization"]
