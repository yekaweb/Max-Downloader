"""User settings utilities"""
import json
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    def __init__(self, settings_file: str = ".settings.json"):
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        if self.settings_file.exists():
            with open(self.settings_file, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()


__all__ = ["SettingsManager"]
