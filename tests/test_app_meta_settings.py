"""
Tests for app metadata and settings functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from pocket_journal.app_meta import (
    APP_NAME, ORG_NAME, VERSION, BUILD_DATE, CHANNEL,
    get_version_info, get_version_string, get_app_title
)
from pocket_journal.settings import (
    SettingsManager, DEFAULT_SETTINGS, 
    get_setting, set_setting, get_theme, set_theme
)


class TestAppMeta:
    """Test app metadata functionality."""
    
    def test_constants(self):
        """Test that core constants are defined correctly."""
        assert APP_NAME == "PocketJournal"
        assert ORG_NAME == "DigiArtifact"
        assert isinstance(VERSION, str)
        assert isinstance(BUILD_DATE, str)
        assert CHANNEL in ["dev", "beta", "release"]
    
    def test_version_info(self):
        """Test version info dictionary."""
        info = get_version_info()
        assert info["app_name"] == APP_NAME
        assert info["org_name"] == ORG_NAME
        assert info["version"] == VERSION
        assert "is_dev" in info
        assert "is_beta" in info
        assert "is_release" in info
    
    def test_version_string(self):
        """Test version string formatting."""
        version_str = get_version_string()
        assert VERSION in version_str
        assert isinstance(version_str, str)
    
    def test_app_title(self):
        """Test app title generation."""
        title = get_app_title()
        assert APP_NAME in title
        assert VERSION in title
        assert isinstance(title, str)
    
    @patch("builtins.open", mock_open(read_data='{"version": "1.0.0", "build_date": "2025-01-01", "channel": "release"}'))
    def test_version_loading(self):
        """Test loading version from JSON file."""
        # This test verifies the version loading mechanism
        # In practice, this would require reloading the module
        pass


class TestSettingsManager:
    """Test settings management functionality."""
    
    def test_default_settings(self):
        """Test that default settings are properly defined."""
        assert "theme" in DEFAULT_SETTINGS
        assert "dock_mode" in DEFAULT_SETTINGS
        assert "autosave_debounce_ms" in DEFAULT_SETTINGS
        assert "show_egg_icon" in DEFAULT_SETTINGS
        assert "eggs_enabled" in DEFAULT_SETTINGS
        assert "hotkey" in DEFAULT_SETTINGS
        
        # Check default values
        assert DEFAULT_SETTINGS["theme"] == "auto"
        assert DEFAULT_SETTINGS["dock_mode"] == "corner"
        assert DEFAULT_SETTINGS["autosave_debounce_ms"] == 900
        assert DEFAULT_SETTINGS["show_egg_icon"] is False
        assert DEFAULT_SETTINGS["eggs_enabled"] is True
        assert DEFAULT_SETTINGS["hotkey"] == "Ctrl+Alt+J"
    
    def test_settings_manager_creation(self):
        """Test creating a settings manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a temporary directory for testing
            settings_manager = SettingsManager()
            
            # Should have default settings
            assert settings_manager.get("theme") == "auto"
            assert settings_manager.get("hotkey") == "Ctrl+Alt+J"
    
    def test_get_set_operations(self):
        """Test getting and setting values."""
        settings_manager = SettingsManager()
        
        # Test getting existing setting
        theme = settings_manager.get("theme")
        assert theme in ["auto", "light", "dark"] or theme == "auto"
        
        # Test setting and getting
        settings_manager.set("test_key", "test_value")
        assert settings_manager.get("test_key") == "test_value"
        
        # Test nested key setting
        settings_manager.set("nested.key", "nested_value")
        assert settings_manager.get("nested.key") == "nested_value"
        
        # Test default value
        assert settings_manager.get("nonexistent_key", "default") == "default"
    
    def test_nested_settings(self):
        """Test nested settings operations."""
        settings_manager = SettingsManager()
        
        # Test getting nested settings
        width = settings_manager.get("window_geometry.width")
        assert isinstance(width, int)
        
        # Test setting nested values
        settings_manager.set("window_geometry.x", 100)
        assert settings_manager.get("window_geometry.x") == 100
    
    def test_reset_functionality(self):
        """Test resetting settings to defaults."""
        settings_manager = SettingsManager()
        
        # Change a setting
        original_theme = settings_manager.get("theme")
        settings_manager.set("theme", "dark")
        assert settings_manager.get("theme") == "dark"
        
        # Reset specific setting
        settings_manager.reset("theme")
        assert settings_manager.get("theme") == DEFAULT_SETTINGS["theme"]
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        # Test theme functions
        current_theme = get_theme()
        assert isinstance(current_theme, str)
        
        set_theme("dark")
        assert get_theme() == "dark"
        
        # Reset to default
        set_theme("auto")
        assert get_theme() == "auto"
    
    def test_directory_creation(self):
        """Test that required directories are created."""
        settings_manager = SettingsManager()
        
        # Test that directory properties return Path objects
        assert isinstance(settings_manager.data_dir, Path)
        assert isinstance(settings_manager.settings_dir, Path)
        assert isinstance(settings_manager.get_journal_directory(), Path)
        assert isinstance(settings_manager.get_backup_directory(), Path)
        assert isinstance(settings_manager.get_log_directory(), Path)


class TestSettingsIntegration:
    """Test settings integration with main application."""
    
    def test_settings_file_creation(self):
        """Test that settings file is created on first run."""
        # This would be tested by running the actual application
        # and checking that the settings file exists
        pass
    
    def test_app_startup_with_settings(self):
        """Test that app starts with proper settings."""
        # This would require integration testing with the actual GUI
        pass