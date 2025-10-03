"""
Tests for Step 10: Settings UI (gear) & toggles

This module tests the comprehensive settings dialog implementation according to
Step 10 requirements.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from PySide6.QtWidgets import QApplication, QWidget, QDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from src.pocket_journal.ui.settings_dialog import SettingsDialog
from src.pocket_journal.settings import settings, set_setting, get_setting


@pytest.fixture
def settings_dialog(qtbot):
    """Create a settings dialog for testing."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    yield dialog
    dialog.close()


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestStep10SettingsDialog:
    """Test Step 10 settings dialog functionality."""
    
    # Step 10 Acceptance Criteria Tests
    
    def test_ac1_settings_tabs_structure(self, settings_dialog):
        """
        AC1: Settings has tabs for General, Docking, Formatting, Files & Exports, 
        Help & Support, Fun (6 total).
        """
        tabs = settings_dialog.tabs
        
        # Check that we have exactly 6 tabs
        assert tabs.count() == 6
        
        # Check tab names match requirements
        expected_tabs = [
            "General", "Docking", "Formatting", 
            "Files & Exports", "Help & Support", "Fun"
        ]
        
        actual_tabs = [tabs.tabText(i) for i in range(tabs.count())]
        assert actual_tabs == expected_tabs
    
    def test_ac2_general_tab_content(self, settings_dialog):
        """
        AC2: General tab contains theme, launch at login, global hotkey settings.
        """
        # Switch to General tab
        settings_dialog.tabs.setCurrentIndex(0)
        
        # Check theme setting
        assert hasattr(settings_dialog, 'theme_combo')
        assert settings_dialog.theme_combo.count() == 3
        assert "Auto (System)" in [settings_dialog.theme_combo.itemText(i) 
                                  for i in range(settings_dialog.theme_combo.count())]
        
        # Check launch at login
        assert hasattr(settings_dialog, 'launch_at_login_checkbox')
        assert settings_dialog.launch_at_login_checkbox.text() == "Launch at login"
        
        # Check global hotkey
        assert hasattr(settings_dialog, 'hotkey_edit')
        assert hasattr(settings_dialog, 'test_hotkey_btn')
        assert settings_dialog.hotkey_edit.placeholderText() == "Ctrl+Alt+J"
    
    def test_ac3_docking_tab_content(self, settings_dialog):
        """
        AC3: Docking tab has corner vs tray options and launcher/panel settings.
        """
        # Switch to Docking tab
        settings_dialog.tabs.setCurrentIndex(1)
        
        # Check dock mode options
        assert hasattr(settings_dialog, 'corner_radio')
        assert hasattr(settings_dialog, 'tray_radio')
        assert settings_dialog.corner_radio.text() == "Corner Launcher"
        assert settings_dialog.tray_radio.text() == "System Tray"
        
        # Check launcher settings
        assert hasattr(settings_dialog, 'circle_size_spin')
        assert hasattr(settings_dialog, 'animation_duration_spin')
        
        # Check panel settings
        assert hasattr(settings_dialog, 'panel_width_spin')
        assert hasattr(settings_dialog, 'panel_height_spin')
        assert hasattr(settings_dialog, 'auto_focus_checkbox')
    
    def test_ac4_formatting_tab_content(self, settings_dialog):
        """
        AC4: Formatting tab has per-rule toggles with enable/disable all buttons.
        """
        # Switch to Formatting tab
        settings_dialog.tabs.setCurrentIndex(2)
        
        # Check formatting checkboxes exist
        assert hasattr(settings_dialog, 'formatting_checkboxes')
        assert len(settings_dialog.formatting_checkboxes) >= 6
        
        # Check specific rules
        expected_rules = [
            "all_caps", "emphatic_exclamation", "important_phrases",
            "parentheticals", "note_lines", "action_lines"
        ]
        
        for rule in expected_rules:
            assert rule in settings_dialog.formatting_checkboxes
        
        # Check enable/disable all buttons
        assert hasattr(settings_dialog, 'enable_all_formatting_btn')
        assert hasattr(settings_dialog, 'disable_all_formatting_btn')
        assert settings_dialog.enable_all_formatting_btn.text() == "Enable All"
        assert settings_dialog.disable_all_formatting_btn.text() == "Disable All"
        
        # Check editor settings
        assert hasattr(settings_dialog, 'font_family_combo')
        assert hasattr(settings_dialog, 'font_size_spin')
        assert hasattr(settings_dialog, 'autosave_spin')
    
    def test_ac5_files_exports_tab_content(self, settings_dialog):
        """
        AC5: Files & Exports tab has data paths and open folder functionality.
        """
        # Switch to Files & Exports tab
        settings_dialog.tabs.setCurrentIndex(3)
        
        # Check data directory settings
        assert hasattr(settings_dialog, 'data_dir_edit')
        assert hasattr(settings_dialog, 'open_data_btn')
        assert hasattr(settings_dialog, 'change_data_dir_btn')
        
        # Check export settings
        assert hasattr(settings_dialog, 'export_format_combo')
        assert hasattr(settings_dialog, 'export_dir_edit')
        assert hasattr(settings_dialog, 'browse_export_dir_btn')
        
        # Check file management
        assert hasattr(settings_dialog, 'open_entries_folder_btn')
        assert hasattr(settings_dialog, 'cleanup_empty_btn')
    
    def test_ac6_help_support_tab_content(self, settings_dialog):
        """
        AC6: Help & Support tab has help/about and diagnostics functionality.
        """
        # Switch to Help & Support tab
        settings_dialog.tabs.setCurrentIndex(4)
        
        # Check help buttons
        assert hasattr(settings_dialog, 'user_guide_btn')
        assert hasattr(settings_dialog, 'keyboard_shortcuts_btn')
        assert hasattr(settings_dialog, 'release_notes_btn')
        
        # Check about buttons
        assert hasattr(settings_dialog, 'about_btn')
        assert hasattr(settings_dialog, 'about_qt_btn')
        
        # Check diagnostics
        assert hasattr(settings_dialog, 'diagnostics_text')
        assert hasattr(settings_dialog, 'refresh_diagnostics_btn')
        assert hasattr(settings_dialog, 'copy_diagnostics_btn')
        assert hasattr(settings_dialog, 'save_diagnostics_btn')
    
    def test_ac7_fun_tab_content(self, settings_dialog):
        """
        AC7: Fun tab has eggs_enabled and show_egg_icon toggles.
        """
        # Switch to Fun tab
        settings_dialog.tabs.setCurrentIndex(5)
        
        # Check easter egg settings
        assert hasattr(settings_dialog, 'eggs_enabled_checkbox')
        assert hasattr(settings_dialog, 'show_egg_icon_checkbox')
        assert settings_dialog.eggs_enabled_checkbox.text() == "Enable easter eggs"
        assert "easter egg icon" in settings_dialog.show_egg_icon_checkbox.text()
        
        # Check fun features
        assert hasattr(settings_dialog, 'fun_animations_checkbox')
        assert hasattr(settings_dialog, 'sound_effects_checkbox')
        
        # Check development settings
        assert hasattr(settings_dialog, 'debug_mode_checkbox')
        assert hasattr(settings_dialog, 'verbose_logging_checkbox')
        assert hasattr(settings_dialog, 'dev_tools_checkbox')
    
    # Component Functionality Tests
    
    def test_immediate_persistence(self, settings_dialog, qtbot):
        """Test that settings changes persist immediately."""
        # Test theme change
        original_theme = get_setting("theme", "Auto (System)")
        settings_dialog.theme_combo.setCurrentText("Dark")
        
        # Setting should be persisted immediately
        assert get_setting("theme") == "Dark"
        
        # Restore original
        set_setting("theme", original_theme)
    
    def test_formatting_rule_toggles(self, settings_dialog, qtbot):
        """Test formatting rule toggle functionality."""
        # Test individual rule toggle
        if "all_caps" in settings_dialog.formatting_checkboxes:
            checkbox = settings_dialog.formatting_checkboxes["all_caps"]
            original_state = checkbox.isChecked()
            
            # Toggle the checkbox
            qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)
            
            # Check setting was updated
            assert get_setting("formatting_rule_all_caps") != original_state
            
            # Restore original state
            checkbox.setChecked(original_state)
    
    def test_enable_disable_all_formatting(self, settings_dialog, qtbot):
        """Test enable/disable all formatting buttons."""
        # Test disable all
        qtbot.mouseClick(settings_dialog.disable_all_formatting_btn, Qt.MouseButton.LeftButton)
        
        # All checkboxes should be unchecked
        for checkbox in settings_dialog.formatting_checkboxes.values():
            assert not checkbox.isChecked()
        
        # Test enable all
        qtbot.mouseClick(settings_dialog.enable_all_formatting_btn, Qt.MouseButton.LeftButton)
        
        # All checkboxes should be checked
        for checkbox in settings_dialog.formatting_checkboxes.values():
            assert checkbox.isChecked()
    
    def test_dock_mode_change(self, settings_dialog, qtbot):
        """Test dock mode change functionality."""
        # Test corner mode
        qtbot.mouseClick(settings_dialog.corner_radio, Qt.MouseButton.LeftButton)
        assert get_setting("dock_mode") == "corner"
        
        # Test tray mode (if available)
        if settings_dialog.tray_radio.isEnabled():
            qtbot.mouseClick(settings_dialog.tray_radio, Qt.MouseButton.LeftButton)
            assert get_setting("dock_mode") == "tray"
    
    @patch('src.pocket_journal.ui.settings_dialog.QFileDialog.getExistingDirectory')
    def test_data_directory_change(self, mock_dialog, settings_dialog, qtbot, temp_data_dir):
        """Test data directory change functionality."""
        mock_dialog.return_value = temp_data_dir
        
        # Click change data directory button
        qtbot.mouseClick(settings_dialog.change_data_dir_btn, Qt.MouseButton.LeftButton)
        
        # Check that setting was updated
        assert get_setting("data_directory") == temp_data_dir
        assert settings_dialog.data_dir_edit.text() == temp_data_dir
    
    def test_global_hotkey_functionality(self, settings_dialog, qtbot):
        """Test global hotkey setting and testing."""
        # Set a hotkey
        settings_dialog.hotkey_edit.setText("Ctrl+Shift+P")
        
        # Trigger text change
        settings_dialog.hotkey_edit.textChanged.emit("Ctrl+Shift+P")
        
        # Check that setting was updated
        assert get_setting("global_hotkey") == "Ctrl+Shift+P"
    
    def test_easter_egg_dependency(self, settings_dialog, qtbot):
        """Test that show_egg_icon depends on eggs_enabled."""
        # Disable easter eggs
        settings_dialog.eggs_enabled_checkbox.setChecked(False)
        settings_dialog.on_eggs_enabled_changed(False)
        
        # show_egg_icon should be disabled and unchecked
        assert not settings_dialog.show_egg_icon_checkbox.isEnabled()
        assert not settings_dialog.show_egg_icon_checkbox.isChecked()
        
        # Re-enable easter eggs
        settings_dialog.eggs_enabled_checkbox.setChecked(True)
        settings_dialog.on_eggs_enabled_changed(True)
        
        # show_egg_icon should be enabled again
        assert settings_dialog.show_egg_icon_checkbox.isEnabled()
    
    def test_diagnostics_functionality(self, settings_dialog, qtbot):
        """Test diagnostics refresh and copy functionality."""
        # Refresh diagnostics
        qtbot.mouseClick(settings_dialog.refresh_diagnostics_btn, Qt.MouseButton.LeftButton)
        
        # Check that diagnostics text is populated
        diagnostics_text = settings_dialog.diagnostics_text.toPlainText()
        assert "System Information:" in diagnostics_text
        assert "OS:" in diagnostics_text
        assert "Python:" in diagnostics_text
        assert "PySide6:" in diagnostics_text
    
    @patch('src.pocket_journal.ui.settings_dialog.QApplication.clipboard')
    def test_copy_diagnostics(self, mock_clipboard, settings_dialog, qtbot):
        """Test copying diagnostics to clipboard."""
        # Setup mock clipboard
        mock_clipboard_obj = Mock()
        mock_clipboard.return_value = mock_clipboard_obj
        
        # Refresh diagnostics first
        settings_dialog.refresh_diagnostics()
        
        # Copy diagnostics
        qtbot.mouseClick(settings_dialog.copy_diagnostics_btn, Qt.MouseButton.LeftButton)
        
        # Check that clipboard.setText was called
        mock_clipboard_obj.setText.assert_called_once()
    
    def test_keyboard_shortcuts_dialog(self, settings_dialog, qtbot):
        """Test keyboard shortcuts dialog display."""
        with patch('src.pocket_journal.ui.settings_dialog.QMessageBox.information') as mock_info:
            qtbot.mouseClick(settings_dialog.keyboard_shortcuts_btn, Qt.MouseButton.LeftButton)
            
            # Check that info dialog was shown
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "Keyboard Shortcuts" in args[1]
            assert "Ctrl+K" in args[2]  # Search shortcut should be documented
    
    def test_reset_functionality(self, settings_dialog, qtbot):
        """Test reset window positions and formatting functionality."""
        with patch('src.pocket_journal.ui.settings_dialog.QMessageBox.question') as mock_question:
            with patch('src.pocket_journal.ui.settings_dialog.QMessageBox.information') as mock_info:
                # Mock user clicking Yes
                mock_question.return_value = QMessageBox.StandardButton.Yes
                
                # Test reset window positions
                qtbot.mouseClick(settings_dialog.reset_window_btn, Qt.MouseButton.LeftButton)
                mock_question.assert_called()
                mock_info.assert_called()
                
                # Reset mocks
                mock_question.reset_mock()
                mock_info.reset_mock()
                
                # Test reset formatting
                qtbot.mouseClick(settings_dialog.reset_formatting_btn, Qt.MouseButton.LeftButton)
                mock_question.assert_called()
                mock_info.assert_called()
    
    def test_signal_emissions(self, settings_dialog, qtbot):
        """Test that appropriate signals are emitted on changes."""
        signal_received = []
        
        # Connect to signals
        settings_dialog.settings_changed.connect(lambda: signal_received.append("settings_changed"))
        settings_dialog.dock_mode_changed.connect(lambda mode: signal_received.append(f"dock_mode:{mode}"))
        
        # Make a change that should emit settings_changed
        settings_dialog.theme_combo.setCurrentText("Dark")
        settings_dialog.on_theme_changed("Dark")
        
        # Make a dock mode change
        if settings_dialog.corner_radio.isEnabled():
            settings_dialog.corner_radio.setChecked(True)
            settings_dialog.on_dock_mode_changed(settings_dialog.corner_radio, True)
        
        # Check signals were emitted
        assert "settings_changed" in signal_received
        assert any("dock_mode:" in signal for signal in signal_received)
    
    # Integration Tests
    
    def test_settings_load_correctly(self, settings_dialog):
        """Test that settings are loaded correctly from configuration."""
        # Set some test values
        set_setting("theme", "Dark")
        set_setting("circle_size", 56)
        set_setting("eggs_enabled", False)
        
        # Create new dialog and load settings
        new_dialog = SettingsDialog()
        
        try:
            # Check that values were loaded correctly
            assert new_dialog.theme_combo.currentText() == "Dark"
            assert new_dialog.circle_size_spin.value() == 56
            assert not new_dialog.eggs_enabled_checkbox.isChecked()
        finally:
            new_dialog.close()
    
    def test_dialog_accept_and_cancel(self, settings_dialog, qtbot):
        """Test dialog accept and cancel functionality."""
        # Test accept
        with patch.object(settings_dialog, 'apply_settings') as mock_apply:
            settings_dialog.accept_settings()
            mock_apply.assert_called_once()
        
        # Dialog should be accepted (would close in real scenario)
        assert settings_dialog.result() == QDialog.DialogCode.Accepted
    
    def test_restore_defaults(self, settings_dialog, qtbot):
        """Test restore defaults functionality."""
        with patch('src.pocket_journal.ui.settings_dialog.QMessageBox.question') as mock_question:
            with patch('src.pocket_journal.ui.settings_dialog.QMessageBox.information') as mock_info:
                with patch.object(settings_dialog, 'load_settings') as mock_load:
                    # Mock user clicking Yes
                    mock_question.return_value = QMessageBox.StandardButton.Yes
                    
                    # Test restore defaults
                    settings_dialog.restore_defaults()
                    
                    # Check that question was asked and settings reloaded
                    mock_question.assert_called()
                    mock_info.assert_called()
                    mock_load.assert_called()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])