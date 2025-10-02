"""
Settings dialog for PocketJournal.

This module provides a comprehensive settings interface for configuring
application behavior, dock mode, startup options, and other preferences.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QButtonGroup, QRadioButton, QTextEdit, QSlider,
    QFileDialog, QMessageBox, QDialogButtonBox, QWidget, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from ..settings import settings, get_setting, set_setting
from ..app_meta import APP_NAME, get_app_title, get_version_string
from .system_tray import StartupManager

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Comprehensive settings dialog for PocketJournal.
    """
    
    # Signals
    settings_changed = Signal()
    dock_mode_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.startup_manager = StartupManager()
        self.pending_changes = {}
        
        self.setup_ui()
        self.load_settings()
        
        # Set dialog properties
        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        logger.debug("Settings dialog initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_general_tab()
        self.create_interface_tab()
        self.create_editor_tab()
        self.create_advanced_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Dock Mode group
        dock_group = QGroupBox("Dock Mode")
        dock_layout = QVBoxLayout(dock_group)
        
        self.dock_button_group = QButtonGroup()
        
        self.corner_radio = QRadioButton("Corner Launcher")
        self.corner_radio.setToolTip("Show floating launcher circle in screen corner")
        self.dock_button_group.addButton(self.corner_radio, 0)
        dock_layout.addWidget(self.corner_radio)
        
        self.tray_radio = QRadioButton("System Tray")
        self.tray_radio.setToolTip("Show icon in system tray instead of corner launcher")
        self.dock_button_group.addButton(self.tray_radio, 1)
        dock_layout.addWidget(self.tray_radio)
        
        # Check if tray is available
        from .system_tray import SystemTrayManager
        if not SystemTrayManager().is_available:
            self.tray_radio.setEnabled(False)
            self.tray_radio.setToolTip("System tray is not available on this system")
        
        dock_info = QLabel("Note: Dock mode changes take effect after application restart.")
        dock_info.setStyleSheet("color: #666; font-style: italic;")
        dock_layout.addWidget(dock_info)
        
        layout.addWidget(dock_group)
        
        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.startup_checkbox = QCheckBox("Launch at Windows startup")
        self.startup_checkbox.setToolTip("Automatically start PocketJournal when Windows starts")
        startup_layout.addWidget(self.startup_checkbox)
        
        if not sys.platform.startswith('win'):
            self.startup_checkbox.setEnabled(False)
            self.startup_checkbox.setToolTip("Startup management is only supported on Windows")
        
        self.startup_status_label = QLabel()
        self.startup_status_label.setStyleSheet("color: #666; font-size: 10px;")
        startup_layout.addWidget(self.startup_status_label)
        
        layout.addWidget(startup_group)
        
        # Theme group
        theme_group = QGroupBox("Appearance")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Light", "Dark"])
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        layout.addWidget(theme_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "General")
    
    def create_interface_tab(self):
        """Create the interface settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Launcher settings
        launcher_group = QGroupBox("Launcher Settings")
        launcher_layout = QGridLayout(launcher_group)
        
        launcher_layout.addWidget(QLabel("Circle Size:"), 0, 0)
        self.circle_size_spin = QSpinBox()
        self.circle_size_spin.setRange(32, 64)
        self.circle_size_spin.setSuffix(" px")
        launcher_layout.addWidget(self.circle_size_spin, 0, 1)
        
        launcher_layout.addWidget(QLabel("Animation Duration:"), 1, 0)
        self.animation_duration_spin = QSpinBox()
        self.animation_duration_spin.setRange(100, 1000)
        self.animation_duration_spin.setSuffix(" ms")
        launcher_layout.addWidget(self.animation_duration_spin, 1, 1)
        
        layout.addWidget(launcher_group)
        
        # Editor Panel settings
        panel_group = QGroupBox("Quick Editor Panel")
        panel_layout = QGridLayout(panel_group)
        
        panel_layout.addWidget(QLabel("Panel Width:"), 0, 0)
        self.panel_width_spin = QSpinBox()
        self.panel_width_spin.setRange(300, 800)
        self.panel_width_spin.setSuffix(" px")
        panel_layout.addWidget(self.panel_width_spin, 0, 1)
        
        panel_layout.addWidget(QLabel("Panel Height:"), 1, 0)
        self.panel_height_spin = QSpinBox()
        self.panel_height_spin.setRange(400, 1000)
        self.panel_height_spin.setSuffix(" px")
        panel_layout.addWidget(self.panel_height_spin, 1, 1)
        
        self.auto_focus_checkbox = QCheckBox("Auto-focus editor when expanded")
        panel_layout.addWidget(self.auto_focus_checkbox, 2, 0, 1, 2)
        
        layout.addWidget(panel_group)
        
        # Window settings
        window_group = QGroupBox("Window Behavior")
        window_layout = QVBoxLayout(window_group)
        
        self.remember_geometry_checkbox = QCheckBox("Remember window positions and sizes")
        window_layout.addWidget(self.remember_geometry_checkbox)
        
        self.minimize_when_panel_checkbox = QCheckBox("Minimize main window when panel is open")
        window_layout.addWidget(self.minimize_when_panel_checkbox)
        
        self.confirm_exit_checkbox = QCheckBox("Confirm before exiting")
        window_layout.addWidget(self.confirm_exit_checkbox)
        
        layout.addWidget(window_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Interface")
    
    def create_editor_tab(self):
        """Create the editor settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QGridLayout(font_group)
        
        font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.setEditable(True)
        # Add common fonts
        fonts = ["Segoe UI", "Arial", "Times New Roman", "Courier New", "Consolas"]
        self.font_family_combo.addItems(fonts)
        font_layout.addWidget(self.font_family_combo, 0, 1)
        
        font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setSuffix(" pt")
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        # Editor behavior
        behavior_group = QGroupBox("Editor Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        # Auto-save settings
        autosave_layout = QHBoxLayout()
        autosave_layout.addWidget(QLabel("Auto-save delay:"))
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(100, 5000)
        self.autosave_spin.setSuffix(" ms")
        autosave_layout.addWidget(self.autosave_spin)
        autosave_layout.addStretch()
        behavior_layout.addLayout(autosave_layout)
        
        self.word_wrap_checkbox = QCheckBox("Word wrap")
        behavior_layout.addWidget(self.word_wrap_checkbox)
        
        self.auto_indent_checkbox = QCheckBox("Auto indent")
        behavior_layout.addWidget(self.auto_indent_checkbox)
        
        self.spell_check_checkbox = QCheckBox("Spell check")
        behavior_layout.addWidget(self.spell_check_checkbox)
        
        layout.addWidget(behavior_group)
        
        # Default content
        content_group = QGroupBox("Default Content")
        content_layout = QVBoxLayout(content_group)
        
        content_layout.addWidget(QLabel("Template for new entries:"))
        self.default_template_combo = QComboBox()
        self.default_template_combo.addItems(["Daily", "Weekly", "Free Form", "Custom"])
        content_layout.addWidget(self.default_template_combo)
        
        self.auto_date_checkbox = QCheckBox("Automatically add date headers")
        content_layout.addWidget(self.auto_date_checkbox)
        
        layout.addWidget(content_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Editor")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Global Hotkey")
        hotkey_layout = QGridLayout(hotkey_group)
        
        hotkey_layout.addWidget(QLabel("Hotkey:"), 0, 0)
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholder("Ctrl+Alt+J")
        hotkey_layout.addWidget(self.hotkey_edit, 0, 1)
        
        hotkey_note = QLabel("Note: Global hotkeys are not yet implemented in this version.")
        hotkey_note.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        hotkey_layout.addWidget(hotkey_note, 1, 0, 1, 2)
        
        layout.addWidget(hotkey_group)
        
        # Data settings
        data_group = QGroupBox("Data Storage")
        data_layout = QVBoxLayout(data_group)
        
        data_location_layout = QHBoxLayout()
        data_location_layout.addWidget(QLabel("Data Directory:"))
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setReadOnly(True)
        data_location_layout.addWidget(self.data_dir_edit)
        
        open_data_button = QPushButton("Open")
        open_data_button.clicked.connect(self.open_data_directory)
        data_location_layout.addWidget(open_data_button)
        
        data_layout.addLayout(data_location_layout)
        
        self.backup_files_checkbox = QCheckBox("Create backup files")
        data_layout.addWidget(self.backup_files_checkbox)
        
        layout.addWidget(data_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug")
        debug_layout = QVBoxLayout(debug_group)
        
        self.show_egg_icon_checkbox = QCheckBox("Show easter egg icon")
        debug_layout.addWidget(self.show_egg_icon_checkbox)
        
        self.eggs_enabled_checkbox = QCheckBox("Enable easter eggs")
        debug_layout.addWidget(self.eggs_enabled_checkbox)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Advanced")
    
    def load_settings(self):
        """Load current settings into the UI."""
        # General tab
        dock_mode = get_setting("dock_mode", "corner")
        if dock_mode == "corner":
            self.corner_radio.setChecked(True)
        else:
            self.tray_radio.setChecked(True)
        
        # Startup setting
        startup_enabled = self.startup_manager.is_startup_enabled()
        self.startup_checkbox.setChecked(startup_enabled)
        self.update_startup_status()
        
        # Theme
        theme = get_setting("theme", "auto")
        theme_index = {"auto": 0, "light": 1, "dark": 2}.get(theme.lower(), 0)
        self.theme_combo.setCurrentIndex(theme_index)
        
        # Interface tab
        self.circle_size_spin.setValue(get_setting("launcher.circle_size", 48))
        self.animation_duration_spin.setValue(get_setting("launcher.animation_duration", 300))
        self.panel_width_spin.setValue(get_setting("editor_panel.width", 480))
        self.panel_height_spin.setValue(get_setting("editor_panel.height", 640))
        self.auto_focus_checkbox.setChecked(get_setting("editor_panel.auto_focus", True))
        self.remember_geometry_checkbox.setChecked(get_setting("remember_window_state", True))
        self.minimize_when_panel_checkbox.setChecked(get_setting("minimize_main_when_panel_open", False))
        self.confirm_exit_checkbox.setChecked(get_setting("confirm_exit", True))
        
        # Editor tab
        self.font_family_combo.setCurrentText(get_setting("font_family", "Segoe UI"))
        self.font_size_spin.setValue(get_setting("font_size", 11))
        self.autosave_spin.setValue(get_setting("autosave_debounce_ms", 900))
        self.word_wrap_checkbox.setChecked(get_setting("word_wrap", True))
        self.auto_indent_checkbox.setChecked(get_setting("auto_indent", True))
        self.spell_check_checkbox.setChecked(get_setting("spell_check", True))
        
        default_template = get_setting("default_template", "daily")
        template_index = {"daily": 0, "weekly": 1, "free form": 2, "custom": 3}.get(default_template.lower(), 0)
        self.default_template_combo.setCurrentIndex(template_index)
        self.auto_date_checkbox.setChecked(get_setting("auto_date_headers", True))
        
        # Advanced tab
        self.hotkey_edit.setText(get_setting("hotkey", "Ctrl+Alt+J"))
        self.data_dir_edit.setText(str(settings.data_dir))
        self.backup_files_checkbox.setChecked(get_setting("backup_files", True))
        self.show_egg_icon_checkbox.setChecked(get_setting("show_egg_icon", False))
        self.eggs_enabled_checkbox.setChecked(get_setting("eggs_enabled", True))
    
    def update_startup_status(self):
        """Update the startup status label."""
        if self.startup_manager.is_startup_enabled():
            command = self.startup_manager.get_startup_command()
            self.startup_status_label.setText(f"Startup command: {command}")
        else:
            self.startup_status_label.setText("Not set to start with Windows")
    
    def open_data_directory(self):
        """Open the data directory in file explorer."""
        import os
        data_dir = settings.data_dir
        
        try:
            if sys.platform.startswith('win'):
                os.startfile(data_dir)
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{data_dir}"')
            else:
                os.system(f'xdg-open "{data_dir}"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open data directory: {e}")
    
    def apply_settings(self):
        """Apply current settings without closing dialog."""
        self.save_settings()
        self.settings_changed.emit()
        
        # Show confirmation
        QMessageBox.information(self, "Settings Applied", 
                               "Settings have been applied successfully.")
    
    def accept_settings(self):
        """Accept and save settings."""
        self.save_settings()
        self.settings_changed.emit()
        self.accept()
    
    def save_settings(self):
        """Save current UI settings."""
        try:
            # General settings
            dock_mode = "corner" if self.corner_radio.isChecked() else "tray"
            current_dock_mode = get_setting("dock_mode", "corner")
            if dock_mode != current_dock_mode:
                set_setting("dock_mode", dock_mode)
                self.dock_mode_changed.emit(dock_mode)
            
            # Handle startup setting
            startup_enabled = self.startup_checkbox.isChecked()
            if startup_enabled != self.startup_manager.is_startup_enabled():
                success = self.startup_manager.set_startup_enabled(startup_enabled)
                if not success:
                    QMessageBox.warning(self, "Startup Setting", 
                                       "Failed to update startup setting. Please run as administrator.")
                else:
                    self.update_startup_status()
            
            # Theme
            themes = ["auto", "light", "dark"]
            theme = themes[self.theme_combo.currentIndex()]
            set_setting("theme", theme)
            
            # Interface settings
            set_setting("launcher.circle_size", self.circle_size_spin.value())
            set_setting("launcher.animation_duration", self.animation_duration_spin.value())
            set_setting("editor_panel.width", self.panel_width_spin.value())
            set_setting("editor_panel.height", self.panel_height_spin.value())
            set_setting("editor_panel.auto_focus", self.auto_focus_checkbox.isChecked())
            set_setting("remember_window_state", self.remember_geometry_checkbox.isChecked())
            set_setting("minimize_main_when_panel_open", self.minimize_when_panel_checkbox.isChecked())
            set_setting("confirm_exit", self.confirm_exit_checkbox.isChecked())
            
            # Editor settings
            set_setting("font_family", self.font_family_combo.currentText())
            set_setting("font_size", self.font_size_spin.value())
            set_setting("autosave_debounce_ms", self.autosave_spin.value())
            set_setting("word_wrap", self.word_wrap_checkbox.isChecked())
            set_setting("auto_indent", self.auto_indent_checkbox.isChecked())
            set_setting("spell_check", self.spell_check_checkbox.isChecked())
            
            templates = ["daily", "weekly", "free form", "custom"]
            template = templates[self.default_template_combo.currentIndex()]
            set_setting("default_template", template)
            set_setting("auto_date_headers", self.auto_date_checkbox.isChecked())
            
            # Advanced settings
            set_setting("hotkey", self.hotkey_edit.text())
            set_setting("backup_files", self.backup_files_checkbox.isChecked())
            set_setting("show_egg_icon", self.show_egg_icon_checkbox.isChecked())
            set_setting("eggs_enabled", self.eggs_enabled_checkbox.isChecked())
            
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def restore_defaults(self):
        """Restore default settings."""
        reply = QMessageBox.question(self, "Restore Defaults",
                                   "Are you sure you want to restore all settings to their defaults?\n"
                                   "This action cannot be undone.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset settings to defaults
            settings.reset()
            
            # Reload UI
            self.load_settings()
            
            QMessageBox.information(self, "Defaults Restored",
                                   "All settings have been restored to their defaults.")


def show_settings_dialog(parent=None) -> Optional[SettingsDialog]:
    """
    Show the settings dialog.
    
    Args:
        parent: Parent widget
        
    Returns:
        The dialog instance if accepted, None if cancelled
    """
    dialog = SettingsDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog
    return None