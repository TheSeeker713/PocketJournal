"""
Settings management for PocketJournal.

This module handles loading, saving, and managing application settings
using platformdirs for cross-platform user data directory access.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from platformdirs import user_data_dir, user_config_dir

from .app_meta import APP_NAME, ORG_NAME

# Set up logging
logger = logging.getLogger(__name__)

# Default application settings
DEFAULT_SETTINGS = {
    "theme": "auto",
    "dock_mode": "corner",
    "autosave_debounce_ms": 900,
    "show_egg_icon": False,
    "eggs_enabled": True,
    "hotkey": "Ctrl+Alt+J",
    
    # Additional UI settings
    "window_geometry": {
        "width": 800,
        "height": 600,
        "x": None,
        "y": None
    },
    "font_family": "Segoe UI",
    "font_size": 11,
    "word_wrap": True,
    "line_numbers": False,
    "spell_check": True,
    
    # Editor settings
    "tab_size": 4,
    "auto_indent": True,
    "show_whitespace": False,
    "highlight_current_line": True,
    
    # Behavior settings
    "auto_save": True,
    "backup_files": True,
    "recent_files_limit": 10,
    "remember_window_state": True,
    "confirm_exit": True,
    
    # Journal-specific settings
    "default_template": "daily",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M",
    "auto_date_headers": True,
    "encrypt_entries": False
}


class SettingsManager:
    """Manages application settings with automatic loading and saving."""
    
    def __init__(self):
        self._settings = DEFAULT_SETTINGS.copy()
        self._settings_dir = Path(user_config_dir(APP_NAME, ORG_NAME))
        self._settings_file = self._settings_dir / "settings.json"
        self._data_dir = Path(user_data_dir(APP_NAME, ORG_NAME))
        
        # Ensure directories exist
        self._settings_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        self.load()
    
    @property
    def settings_file(self) -> Path:
        """Get the path to the settings file."""
        return self._settings_file
    
    @property
    def data_dir(self) -> Path:
        """Get the path to the user data directory."""
        return self._data_dir
    
    @property
    def settings_dir(self) -> Path:
        """Get the path to the settings directory."""
        return self._settings_dir
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key, with optional default."""
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value by key."""
        keys = key.split('.')
        setting = self._settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in setting:
                setting[k] = {}
            setting = setting[k]
        
        # Set the value
        setting[keys[-1]] = value
        
        # Auto-save after setting
        self.save()
    
    def update(self, settings: Dict[str, Any]) -> None:
        """Update multiple settings at once."""
        def deep_update(d: Dict, u: Dict) -> Dict:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        deep_update(self._settings, settings)
        self.save()
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset a specific setting or all settings to defaults."""
        if key is None:
            # Reset all settings
            self._settings = DEFAULT_SETTINGS.copy()
        else:
            # Reset specific setting
            keys = key.split('.')
            default_value = DEFAULT_SETTINGS
            
            try:
                for k in keys:
                    default_value = default_value[k]
                self.set(key, default_value)
            except (KeyError, TypeError):
                logger.warning(f"Cannot reset unknown setting key: {key}")
                return
        
        self.save()
    
    def load(self) -> bool:
        """Load settings from file. Returns True if successful."""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys are present
                self._merge_with_defaults(loaded_settings)
                logger.info(f"Settings loaded from {self._settings_file}")
                return True
            else:
                # First run - create default settings file
                logger.info("Settings file not found, creating with defaults")
                self.save()
                return True
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load settings from {self._settings_file}: {e}")
            logger.info("Using default settings")
            return False
    
    def save(self) -> bool:
        """Save current settings to file. Returns True if successful."""
        try:
            # Ensure directory exists
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Settings saved to {self._settings_file}")
            return True
            
        except (IOError, TypeError) as e:
            logger.error(f"Failed to save settings to {self._settings_file}: {e}")
            return False
    
    def _merge_with_defaults(self, loaded_settings: Dict[str, Any]) -> None:
        """Merge loaded settings with defaults, preserving user values."""
        def merge_dict(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._settings = merge_dict(DEFAULT_SETTINGS, loaded_settings)
    
    def get_journal_directory(self) -> Path:
        """Get the default directory for journal files."""
        journal_dir = self._data_dir / "journals"
        journal_dir.mkdir(parents=True, exist_ok=True)
        return journal_dir
    
    def get_backup_directory(self) -> Path:
        """Get the directory for backup files."""
        backup_dir = self._data_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def get_log_directory(self) -> Path:
        """Get the directory for log files."""
        log_dir = self._data_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def export_settings(self, file_path: Union[str, Path]) -> bool:
        """Export current settings to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings exported to {file_path}")
            return True
        except (IOError, TypeError) as e:
            logger.error(f"Failed to export settings to {file_path}: {e}")
            return False
    
    def import_settings(self, file_path: Union[str, Path]) -> bool:
        """Import settings from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            self._merge_with_defaults(imported_settings)
            self.save()
            logger.info(f"Settings imported from {file_path}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to import settings from {file_path}: {e}")
            return False


# Global settings instance
settings = SettingsManager()


# Convenience functions for common operations
def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value (convenience function)."""
    return settings.get(key, default)


def set_setting(key: str, value: Any) -> None:
    """Set a setting value (convenience function)."""
    settings.set(key, value)


def get_theme() -> str:
    """Get the current theme setting."""
    return settings.get("theme", "auto")


def set_theme(theme: str) -> None:
    """Set the theme setting."""
    settings.set("theme", theme)


def get_hotkey() -> str:
    """Get the global hotkey setting."""
    return settings.get("hotkey", "Ctrl+Alt+J")


def set_hotkey(hotkey: str) -> None:
    """Set the global hotkey setting."""
    settings.set("hotkey", hotkey)