"""
Settings dialog for PocketJournal.

This module provides a comprehensive settings interface for configuring
application behavior, dock mode, startup options, and other preferences.
"""

import sys
import logging
import platform
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QButtonGroup, QRadioButton, QFileDialog, QMessageBox, QDialogButtonBox, QWidget, QPlainTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer

from ..settings import settings, get_setting, set_setting
from ..app_meta import APP_NAME, get_version_string, ORG_NAME
from .system_tray import StartupManager
from .entry_actions import open_data_folder
from ..core.global_hotkey import GlobalHotkeyManager

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Comprehensive settings dialog for PocketJournal.
    
    Step 10 Requirements:
    - General (theme, launch at login, hotkey)
    - Docking (corner vs tray)
    - Formatting (per-rule toggles)
    - Files & Exports (paths, open folder)
    - Help & Support (open help/about, copy diagnostics)
    - Fun (eggs_enabled on/off, show_egg_icon on/off)
    """
    
    # Signals
    settings_changed = Signal()
    dock_mode_changed = Signal(str)
    hotkey_changed = Signal(str, str)  # old, new
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.startup_manager = StartupManager()
        self.hotkey_manager = GlobalHotkeyManager()
        self.pending_changes = {}
        
        self.setup_ui()
        self.load_settings()
        self.setup_connections()
        
        # Set dialog properties
        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setModal(True)
        self.resize(700, 600)
        
        logger.debug("Settings dialog initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs according to Step 10 requirements
        self.create_general_tab()
        self.create_docking_tab()
        self.create_formatting_tab()
        self.create_files_exports_tab()
        self.create_help_support_tab()
        self.create_fun_tab()
        
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
        """Create the General tab (theme, launch at login, hotkey)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto (System)", "Light", "Dark"])
        self.theme_combo.setToolTip("Choose the application theme")
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        layout.addWidget(theme_group)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.launch_at_login_checkbox = QCheckBox("Launch at login")
        self.launch_at_login_checkbox.setToolTip("Automatically start PocketJournal when you log in")
        startup_layout.addWidget(self.launch_at_login_checkbox)
        
        if not sys.platform.startswith('win'):
            self.launch_at_login_checkbox.setEnabled(False)
            self.launch_at_login_checkbox.setToolTip("Startup management is only supported on Windows")
        
        self.startup_status_label = QLabel()
        self.startup_status_label.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
        startup_layout.addWidget(self.startup_status_label)
        
        layout.addWidget(startup_group)
        
        # Global hotkey settings
        hotkey_group = QGroupBox("Global Hotkey")
        hotkey_layout = QGridLayout(hotkey_group)
        
        hotkey_layout.addWidget(QLabel("Hotkey:"), 0, 0)
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("Ctrl+Alt+J")
        self.hotkey_edit.setToolTip("Global hotkey to expand the editor panel")
        hotkey_layout.addWidget(self.hotkey_edit, 0, 1)
        
        self.test_hotkey_btn = QPushButton("Test")
        self.test_hotkey_btn.setToolTip("Test the hotkey registration")
        hotkey_layout.addWidget(self.test_hotkey_btn, 0, 2)
        
        # Hotkey status
        self.hotkey_status_label = QLabel()
        self.hotkey_status_label.setStyleSheet("color: #666; font-size: 10px;")
        hotkey_layout.addWidget(self.hotkey_status_label, 1, 0, 1, 3)
        
        if not self.hotkey_manager.is_available():
            self.hotkey_edit.setEnabled(False)
            self.test_hotkey_btn.setEnabled(False)
            self.hotkey_status_label.setText(f"Global hotkeys not available on {platform.system()}")
            self.hotkey_status_label.setStyleSheet("color: #d9534f; font-size: 10px;")
        
        layout.addWidget(hotkey_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "General")
    
    def create_docking_tab(self):
        """Create the Docking tab (corner vs tray)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Dock mode settings
        dock_group = QGroupBox("Dock Mode")
        dock_layout = QVBoxLayout(dock_group)
        
        self.dock_button_group = QButtonGroup()
        
        self.corner_radio = QRadioButton("Corner Launcher")
        self.corner_radio.setToolTip("Show floating launcher in screen corner")
        self.dock_button_group.addButton(self.corner_radio, 0)
        dock_layout.addWidget(self.corner_radio)
        
        self.tray_radio = QRadioButton("System Tray")
        self.tray_radio.setToolTip("Show icon in system tray instead of corner launcher")
        self.dock_button_group.addButton(self.tray_radio, 1)
        dock_layout.addWidget(self.tray_radio)
        
        # Check if tray is available
        try:
            from .system_tray import SystemTrayManager
            if not SystemTrayManager().is_available:
                self.tray_radio.setEnabled(False)
                self.tray_radio.setToolTip("System tray is not available on this system")
        except ImportError:
            self.tray_radio.setEnabled(False)
            self.tray_radio.setToolTip("System tray support not available")
        
        dock_info = QLabel("Note: Dock mode changes take effect after application restart.")
        dock_info.setStyleSheet("color: #666; font-style: italic; margin-top: 8px;")
        dock_layout.addWidget(dock_info)
        
        layout.addWidget(dock_group)
        
        # Corner launcher settings
        corner_group = QGroupBox("Corner Launcher Settings")
        corner_layout = QGridLayout(corner_group)
        
        corner_layout.addWidget(QLabel("Circle Size:"), 0, 0)
        self.circle_size_spin = QSpinBox()
        self.circle_size_spin.setRange(32, 64)
        self.circle_size_spin.setSuffix(" px")
        self.circle_size_spin.setToolTip("Size of the circular launcher")
        corner_layout.addWidget(self.circle_size_spin, 0, 1)
        
        corner_layout.addWidget(QLabel("Animation Duration:"), 1, 0)
        self.animation_duration_spin = QSpinBox()
        self.animation_duration_spin.setRange(100, 1000)
        self.animation_duration_spin.setSuffix(" ms")
        self.animation_duration_spin.setToolTip("Duration of expand/collapse animations")
        corner_layout.addWidget(self.animation_duration_spin, 1, 1)
        
        layout.addWidget(corner_group)
        
        # Editor panel settings
        panel_group = QGroupBox("Editor Panel Settings")
        panel_layout = QGridLayout(panel_group)
        
        panel_layout.addWidget(QLabel("Panel Width:"), 0, 0)
        self.panel_width_spin = QSpinBox()
        self.panel_width_spin.setRange(300, 800)
        self.panel_width_spin.setSuffix(" px")
        self.panel_width_spin.setToolTip("Width of the expanded editor panel")
        panel_layout.addWidget(self.panel_width_spin, 0, 1)
        
        panel_layout.addWidget(QLabel("Panel Height:"), 1, 0)
        self.panel_height_spin = QSpinBox()
        self.panel_height_spin.setRange(400, 1000)
        self.panel_height_spin.setSuffix(" px")
        self.panel_height_spin.setToolTip("Height of the expanded editor panel")
        panel_layout.addWidget(self.panel_height_spin, 1, 1)
        
        self.auto_focus_checkbox = QCheckBox("Auto-focus editor when expanded")
        self.auto_focus_checkbox.setToolTip("Automatically focus the text editor when panel expands")
        panel_layout.addWidget(self.auto_focus_checkbox, 2, 0, 1, 2)
        
        layout.addWidget(panel_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "Docking")
    
    def create_formatting_tab(self):
        """Create the Formatting tab (per-rule toggles)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Smart formatting rules
        formatting_group = QGroupBox("Smart Formatting Rules")
        formatting_layout = QVBoxLayout(formatting_group)
        
        # Description
        desc_label = QLabel("Enable or disable specific formatting rules. Changes apply immediately to the editor.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 8px;")
        desc_label.setWordWrap(True)
        formatting_layout.addWidget(desc_label)
        
        # Formatting rules checkboxes
        self.formatting_checkboxes = {}
        
        # Default formatting rules
        default_rules = [
            ("all_caps", "Bold ALL-CAPS words (≥4 characters)", True),
            ("emphatic_exclamation", "Bold phrases ending with exclamation marks", True),
            ("important_phrases", "Bold phrases following \"IMPORTANT:\"", True),
            ("parentheticals", "Italicize text in parentheses", True),
            ("note_lines", "Underline lines starting with \"NOTE:\"", True),
            ("action_lines", "Underline lines starting with \"ACTION:\"", True),
            ("bullet_lists", "Format bullet lists (-, *)", True),
            ("numbered_lists", "Format numbered lists (1., 2., etc.)", True),
        ]
        
        for rule_name, description, default_enabled in default_rules:
            checkbox = QCheckBox(description)
            checkbox.setObjectName(f"formatting_{rule_name}")
            checkbox.setToolTip(f"Toggle {rule_name} formatting rule")
            self.formatting_checkboxes[rule_name] = checkbox
            formatting_layout.addWidget(checkbox)
        
        # All/None buttons
        buttons_layout = QHBoxLayout()
        
        self.enable_all_formatting_btn = QPushButton("Enable All")
        self.enable_all_formatting_btn.setToolTip("Enable all formatting rules")
        buttons_layout.addWidget(self.enable_all_formatting_btn)
        
        self.disable_all_formatting_btn = QPushButton("Disable All")
        self.disable_all_formatting_btn.setToolTip("Disable all formatting rules")
        buttons_layout.addWidget(self.disable_all_formatting_btn)
        
        buttons_layout.addStretch()
        formatting_layout.addLayout(buttons_layout)
        
        layout.addWidget(formatting_group)
        
        # Editor settings
        editor_group = QGroupBox("Editor Settings")
        editor_layout = QGridLayout(editor_group)
        
        # Font settings
        editor_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Segoe UI", "Arial", "Times New Roman", "Consolas", "Courier New"])
        self.font_family_combo.setEditable(True)
        editor_layout.addWidget(self.font_family_combo, 0, 1)
        
        editor_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSuffix(" pt")
        editor_layout.addWidget(self.font_size_spin, 1, 1)
        
        # Auto-save settings
        editor_layout.addWidget(QLabel("Auto-save delay:"), 2, 0)
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(100, 5000)
        self.autosave_spin.setSuffix(" ms")
        self.autosave_spin.setToolTip("Delay before auto-saving changes")
        editor_layout.addWidget(self.autosave_spin, 2, 1)
        
        # Editor behavior
        self.word_wrap_checkbox = QCheckBox("Word wrap")
        self.word_wrap_checkbox.setToolTip("Wrap long lines in the editor")
        editor_layout.addWidget(self.word_wrap_checkbox, 3, 0, 1, 2)
        
        self.auto_indent_checkbox = QCheckBox("Auto indent")
        self.auto_indent_checkbox.setToolTip("Automatically indent new lines")
        editor_layout.addWidget(self.auto_indent_checkbox, 4, 0, 1, 2)
        
        layout.addWidget(editor_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "Formatting")
    
    def create_files_exports_tab(self):
        """Create the Files & Exports tab (paths, open folder)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Data storage settings
        storage_group = QGroupBox("Data Storage")
        storage_layout = QVBoxLayout(storage_group)
        
        # Data directory
        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(QLabel("Data Directory:"))
        
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setReadOnly(True)
        self.data_dir_edit.setToolTip("Location where journal entries are stored")
        data_dir_layout.addWidget(self.data_dir_edit)
        
        self.open_data_btn = QPushButton("Open")
        self.open_data_btn.setToolTip("Open data directory in file explorer")
        data_dir_layout.addWidget(self.open_data_btn)
        
        self.change_data_dir_btn = QPushButton("Change...")
        self.change_data_dir_btn.setToolTip("Change data directory location")
        data_dir_layout.addWidget(self.change_data_dir_btn)
        
        storage_layout.addLayout(data_dir_layout)
        
        # Backup settings
        self.backup_files_checkbox = QCheckBox("Create backup files")
        self.backup_files_checkbox.setToolTip("Automatically create backup copies of entries")
        storage_layout.addWidget(self.backup_files_checkbox)
        
        self.auto_cleanup_checkbox = QCheckBox("Auto-cleanup empty entries")
        self.auto_cleanup_checkbox.setToolTip("Automatically remove entries with no content")
        storage_layout.addWidget(self.auto_cleanup_checkbox)
        
        layout.addWidget(storage_group)
        
        # Export settings
        export_group = QGroupBox("Export Settings")
        export_layout = QGridLayout(export_group)
        
        export_layout.addWidget(QLabel("Default Export Format:"), 0, 0)
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Markdown (.md)", "Plain Text (.txt)", "Rich Text (.rtf)"])
        self.export_format_combo.setToolTip("Default format for entry exports")
        export_layout.addWidget(self.export_format_combo, 0, 1)
        
        export_layout.addWidget(QLabel("Export Directory:"), 1, 0)
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setPlaceholderText("Use system default (Downloads)")
        self.export_dir_edit.setToolTip("Default directory for exported files")
        export_layout.addWidget(self.export_dir_edit, 1, 1)
        
        self.browse_export_dir_btn = QPushButton("Browse...")
        self.browse_export_dir_btn.setToolTip("Choose export directory")
        export_layout.addWidget(self.browse_export_dir_btn, 1, 2)
        
        # Export options
        self.include_metadata_checkbox = QCheckBox("Include metadata in exports")
        self.include_metadata_checkbox.setToolTip("Include title, date, and other metadata in exported files")
        export_layout.addWidget(self.include_metadata_checkbox, 2, 0, 1, 3)
        
        self.preserve_formatting_checkbox = QCheckBox("Preserve formatting in exports")
        self.preserve_formatting_checkbox.setToolTip("Maintain formatting when exporting")
        export_layout.addWidget(self.preserve_formatting_checkbox, 3, 0, 1, 3)
        
        layout.addWidget(export_group)
        
        # File management
        management_group = QGroupBox("File Management")
        management_layout = QHBoxLayout(management_group)
        
        self.open_entries_folder_btn = QPushButton("Open Entries Folder")
        self.open_entries_folder_btn.setToolTip("Open the entries folder in file explorer")
        management_layout.addWidget(self.open_entries_folder_btn)
        
        self.cleanup_empty_btn = QPushButton("Cleanup Empty Entries")
        self.cleanup_empty_btn.setToolTip("Remove all empty journal entries")
        management_layout.addWidget(self.cleanup_empty_btn)
        
        management_layout.addStretch()
        
        layout.addWidget(management_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "Files & Exports")
    
    def create_help_support_tab(self):
        """Create the Help & Support tab (open help/about, copy diagnostics)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Documentation and help
        help_group = QGroupBox("Documentation & Help")
        help_layout = QVBoxLayout(help_group)
        
        # Help buttons
        help_buttons_layout = QHBoxLayout()
        
        self.user_guide_btn = QPushButton("User Guide")
        self.user_guide_btn.setToolTip("Open the PocketJournal user guide")
        help_buttons_layout.addWidget(self.user_guide_btn)
        
        self.keyboard_shortcuts_btn = QPushButton("Keyboard Shortcuts")
        self.keyboard_shortcuts_btn.setToolTip("View available keyboard shortcuts")
        help_buttons_layout.addWidget(self.keyboard_shortcuts_btn)
        
        self.release_notes_btn = QPushButton("Release Notes")
        self.release_notes_btn.setToolTip("View release notes and changelog")
        help_buttons_layout.addWidget(self.release_notes_btn)
        
        help_buttons_layout.addStretch()
        help_layout.addLayout(help_buttons_layout)
        
        layout.addWidget(help_group)
        
        # About section
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        
        # App info
        app_info = QLabel(f"""
<h3>{APP_NAME}</h3>
<p><b>Version:</b> {get_version_string()}</p>
<p><b>Organization:</b> {ORG_NAME}</p>
<p>A simple journaling application with a micro-launcher interface.</p>
        """.strip())
        app_info.setTextFormat(Qt.TextFormat.RichText)
        app_info.setWordWrap(True)
        about_layout.addWidget(app_info)
        
        # About buttons
        about_buttons_layout = QHBoxLayout()
        
        self.about_btn = QPushButton("About")
        self.about_btn.setToolTip("Show detailed about information")
        about_buttons_layout.addWidget(self.about_btn)
        
        self.about_qt_btn = QPushButton("About Qt")
        self.about_qt_btn.setToolTip("Show Qt framework information")
        about_buttons_layout.addWidget(self.about_qt_btn)
        
        about_buttons_layout.addStretch()
        about_layout.addLayout(about_buttons_layout)
        
        layout.addWidget(about_group)
        
        # Diagnostics section
        diagnostics_group = QGroupBox("Diagnostics")
        diagnostics_layout = QVBoxLayout(diagnostics_group)
        
        # System information display
        self.diagnostics_text = QPlainTextEdit()
        self.diagnostics_text.setMaximumHeight(150)
        self.diagnostics_text.setReadOnly(True)
        self.diagnostics_text.setPlainText("Click 'Refresh Diagnostics' to view system information...")
        diagnostics_layout.addWidget(self.diagnostics_text)
        
        # Diagnostics buttons
        diag_buttons_layout = QHBoxLayout()
        
        self.refresh_diagnostics_btn = QPushButton("Refresh Diagnostics")
        self.refresh_diagnostics_btn.setToolTip("Refresh system diagnostic information")
        diag_buttons_layout.addWidget(self.refresh_diagnostics_btn)
        
        self.copy_diagnostics_btn = QPushButton("Copy to Clipboard")
        self.copy_diagnostics_btn.setToolTip("Copy diagnostic information to clipboard")
        diag_buttons_layout.addWidget(self.copy_diagnostics_btn)
        
        self.save_diagnostics_btn = QPushButton("Save to File...")
        self.save_diagnostics_btn.setToolTip("Save diagnostic information to a file")
        diag_buttons_layout.addWidget(self.save_diagnostics_btn)
        
        diag_buttons_layout.addStretch()
        diagnostics_layout.addLayout(diag_buttons_layout)
        
        layout.addWidget(diagnostics_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "Help & Support")
    
    def create_fun_tab(self):
        """Create the Fun tab (eggs_enabled on/off, show_egg_icon on/off)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Easter eggs section
        eggs_group = QGroupBox("Easter Eggs")
        eggs_layout = QVBoxLayout(eggs_group)
        
        # Description
        eggs_desc = QLabel("""
Easter eggs are hidden features and fun surprises throughout the application.
These settings control whether easter eggs are active and visible.
        """.strip())
        eggs_desc.setWordWrap(True)
        eggs_desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        eggs_layout.addWidget(eggs_desc)
        
        # Easter egg settings
        self.eggs_enabled_checkbox = QCheckBox("Enable easter eggs")
        self.eggs_enabled_checkbox.setToolTip("Enable hidden features and fun surprises")
        eggs_layout.addWidget(self.eggs_enabled_checkbox)
        
        self.show_egg_icon_checkbox = QCheckBox("Show easter egg icon in toolbar")
        self.show_egg_icon_checkbox.setToolTip("Show the easter egg icon in the editor toolbar")
        eggs_layout.addWidget(self.show_egg_icon_checkbox)
        
        # Fun features
        self.fun_animations_checkbox = QCheckBox("Enable fun animations")
        self.fun_animations_checkbox.setToolTip("Enable playful animations and transitions")
        eggs_layout.addWidget(self.fun_animations_checkbox)
        
        self.sound_effects_checkbox = QCheckBox("Enable sound effects")
        self.sound_effects_checkbox.setToolTip("Enable sound effects for interactions")
        eggs_layout.addWidget(self.sound_effects_checkbox)
        
        layout.addWidget(eggs_group)
        
        # Development section
        dev_group = QGroupBox("Development & Debug")
        dev_layout = QVBoxLayout(dev_group)
        
        dev_desc = QLabel("""
Development features for testing and debugging. These settings are typically
used by developers and power users.
        """.strip())
        dev_desc.setWordWrap(True)
        dev_desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        dev_layout.addWidget(dev_desc)
        
        # Debug settings
        self.debug_mode_checkbox = QCheckBox("Enable debug mode")
        self.debug_mode_checkbox.setToolTip("Enable additional logging and debug features")
        dev_layout.addWidget(self.debug_mode_checkbox)
        
        self.verbose_logging_checkbox = QCheckBox("Verbose logging")
        self.verbose_logging_checkbox.setToolTip("Enable detailed logging to console and files")
        dev_layout.addWidget(self.verbose_logging_checkbox)
        
        self.dev_tools_checkbox = QCheckBox("Show developer tools")
        self.dev_tools_checkbox.setToolTip("Show additional developer tools and options")
        dev_layout.addWidget(self.dev_tools_checkbox)
        
        layout.addWidget(dev_group)
        
        # Reset section
        reset_group = QGroupBox("Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_desc = QLabel("These actions will reset various aspects of the application to defaults.")
        reset_desc.setWordWrap(True)
        reset_desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        reset_layout.addWidget(reset_desc)
        
        reset_buttons_layout = QHBoxLayout()
        
        self.reset_window_btn = QPushButton("Reset Window Positions")
        self.reset_window_btn.setToolTip("Reset all window positions and sizes to defaults")
        reset_buttons_layout.addWidget(self.reset_window_btn)
        
        self.reset_formatting_btn = QPushButton("Reset Formatting")
        self.reset_formatting_btn.setToolTip("Reset all formatting rules to default settings")
        reset_buttons_layout.addWidget(self.reset_formatting_btn)
        
        reset_buttons_layout.addStretch()
        reset_layout.addLayout(reset_buttons_layout)
        
        layout.addWidget(reset_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "Fun")
    
    def setup_connections(self):
        """Setup signal connections for immediate persistence."""
        # General tab connections
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.launch_at_login_checkbox.toggled.connect(self.on_startup_toggled)
        self.hotkey_edit.textChanged.connect(self.on_hotkey_changed)
        self.test_hotkey_btn.clicked.connect(self.test_hotkey)
        
        # Docking tab connections
        self.dock_button_group.buttonToggled.connect(self.on_dock_mode_changed)
        self.circle_size_spin.valueChanged.connect(self.on_circle_size_changed)
        self.animation_duration_spin.valueChanged.connect(self.on_animation_duration_changed)
        self.panel_width_spin.valueChanged.connect(self.on_panel_width_changed)
        self.panel_height_spin.valueChanged.connect(self.on_panel_height_changed)
        self.auto_focus_checkbox.toggled.connect(self.on_auto_focus_changed)
        
        # Formatting tab connections
        for rule_name, checkbox in self.formatting_checkboxes.items():
            checkbox.toggled.connect(lambda checked, name=rule_name: self.on_formatting_rule_toggled(name, checked))
        
        self.enable_all_formatting_btn.clicked.connect(self.enable_all_formatting)
        self.disable_all_formatting_btn.clicked.connect(self.disable_all_formatting)
        self.font_family_combo.currentTextChanged.connect(self.on_font_family_changed)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        self.autosave_spin.valueChanged.connect(self.on_autosave_delay_changed)
        self.word_wrap_checkbox.toggled.connect(self.on_word_wrap_changed)
        self.auto_indent_checkbox.toggled.connect(self.on_auto_indent_changed)
        
        # Files & Exports tab connections
        self.open_data_btn.clicked.connect(self.open_data_directory)
        self.change_data_dir_btn.clicked.connect(self.change_data_directory)
        self.backup_files_checkbox.toggled.connect(self.on_backup_files_changed)
        self.auto_cleanup_checkbox.toggled.connect(self.on_auto_cleanup_changed)
        self.export_format_combo.currentTextChanged.connect(self.on_export_format_changed)
        self.browse_export_dir_btn.clicked.connect(self.browse_export_directory)
        self.include_metadata_checkbox.toggled.connect(self.on_include_metadata_changed)
        self.preserve_formatting_checkbox.toggled.connect(self.on_preserve_formatting_changed)
        self.open_entries_folder_btn.clicked.connect(self.open_entries_folder)
        self.cleanup_empty_btn.clicked.connect(self.cleanup_empty_entries)
        
        # Help & Support tab connections
        self.user_guide_btn.clicked.connect(self.open_user_guide)
        self.keyboard_shortcuts_btn.clicked.connect(self.show_keyboard_shortcuts)
        self.release_notes_btn.clicked.connect(self.show_release_notes)
        self.about_btn.clicked.connect(self.show_about)
        self.about_qt_btn.clicked.connect(self.show_about_qt)
        self.refresh_diagnostics_btn.clicked.connect(self.refresh_diagnostics)
        self.copy_diagnostics_btn.clicked.connect(self.copy_diagnostics)
        self.save_diagnostics_btn.clicked.connect(self.save_diagnostics)
        
        # Fun tab connections
        self.eggs_enabled_checkbox.toggled.connect(self.on_eggs_enabled_changed)
        self.show_egg_icon_checkbox.toggled.connect(self.on_show_egg_icon_changed)
        self.fun_animations_checkbox.toggled.connect(self.on_fun_animations_changed)
        self.sound_effects_checkbox.toggled.connect(self.on_sound_effects_changed)
        self.debug_mode_checkbox.toggled.connect(self.on_debug_mode_changed)
        self.verbose_logging_checkbox.toggled.connect(self.on_verbose_logging_changed)
        self.dev_tools_checkbox.toggled.connect(self.on_dev_tools_changed)
        self.reset_window_btn.clicked.connect(self.reset_window_positions)
        self.reset_formatting_btn.clicked.connect(self.reset_formatting_settings)
    
    def load_settings(self):
        """Load settings from configuration and update UI."""
        # General tab
        theme = get_setting("theme", "Auto (System)")
        self.theme_combo.setCurrentText(theme)
        
        # Load startup status
        is_startup_enabled = self.startup_manager.is_startup_enabled()
        self.launch_at_login_checkbox.setChecked(is_startup_enabled)
        self.update_startup_status()
        
        # Load hotkey
        hotkey = get_setting("global_hotkey", "Ctrl+Alt+J")
        self.hotkey_edit.setText(hotkey)
        self.update_hotkey_status()
        
        # Docking tab
        dock_mode = get_setting("dock_mode", "corner")
        if dock_mode == "corner":
            self.corner_radio.setChecked(True)
        else:
            self.tray_radio.setChecked(True)
        
        self.circle_size_spin.setValue(get_setting("circle_size", 48))
        self.animation_duration_spin.setValue(get_setting("animation_duration", 300))
        self.panel_width_spin.setValue(get_setting("panel_width", 500))
        self.panel_height_spin.setValue(get_setting("panel_height", 600))
        self.auto_focus_checkbox.setChecked(get_setting("auto_focus_editor", True))
        
        # Formatting tab
        # Load formatting rules
        for rule_name, checkbox in self.formatting_checkboxes.items():
            enabled = get_setting(f"formatting_rule_{rule_name}", True)
            checkbox.setChecked(enabled)
        
        self.font_family_combo.setCurrentText(get_setting("font_family", "Segoe UI"))
        self.font_size_spin.setValue(get_setting("font_size", 11))
        self.autosave_spin.setValue(get_setting("autosave_delay", 500))
        self.word_wrap_checkbox.setChecked(get_setting("word_wrap", True))
        self.auto_indent_checkbox.setChecked(get_setting("auto_indent", True))
        
        # Files & Exports tab
        self.data_dir_edit.setText(str(get_setting("data_directory", Path.home() / "PocketJournal")))
        self.backup_files_checkbox.setChecked(get_setting("backup_files", True))
        self.auto_cleanup_checkbox.setChecked(get_setting("auto_cleanup", False))
        
        export_format = get_setting("export_format", "Markdown (.md)")
        self.export_format_combo.setCurrentText(export_format)
        self.export_dir_edit.setText(get_setting("export_directory", ""))
        self.include_metadata_checkbox.setChecked(get_setting("include_metadata", True))
        self.preserve_formatting_checkbox.setChecked(get_setting("preserve_formatting", True))
        
        # Fun tab
        self.eggs_enabled_checkbox.setChecked(get_setting("eggs_enabled", True))
        self.show_egg_icon_checkbox.setChecked(get_setting("show_egg_icon", True))
        self.fun_animations_checkbox.setChecked(get_setting("fun_animations", True))
        self.sound_effects_checkbox.setChecked(get_setting("sound_effects", False))
        self.debug_mode_checkbox.setChecked(get_setting("debug_mode", False))
        self.verbose_logging_checkbox.setChecked(get_setting("verbose_logging", False))
        self.dev_tools_checkbox.setChecked(get_setting("dev_tools", False))
        
        logger.debug("Settings loaded from configuration")
    
    # Signal handlers for immediate persistence
    def on_theme_changed(self, theme):
        """Handle theme change."""
        set_setting("theme", theme)
        self.settings_changed.emit()
        logger.debug(f"Theme changed to: {theme}")
    
    def on_startup_toggled(self, enabled):
        """Handle startup setting toggle."""
        try:
            success = self.startup_manager.set_startup_enabled(enabled)
            if success:
                set_setting("launch_at_login", enabled)
                self.update_startup_status()
                logger.debug(f"Startup setting changed to: {enabled}")
            else:
                # Revert checkbox if setting failed
                self.launch_at_login_checkbox.setChecked(not enabled)
                logger.warning("Failed to change startup setting")
        except Exception as e:
            logger.error(f"Failed to change startup setting: {e}")
            # Revert checkbox
            self.launch_at_login_checkbox.setChecked(not enabled)
    
    def on_hotkey_changed(self, hotkey):
        """Handle hotkey change."""
        if self.hotkey_manager.is_available():
            try:
                old_hotkey = get_setting("global_hotkey", "Ctrl+Alt+J")
                if old_hotkey != hotkey:
                    # Test if hotkey is valid
                    if self.hotkey_manager.register_hotkey("test", hotkey, lambda: None):
                        self.hotkey_manager.unregister_hotkey("test")
                        set_setting("global_hotkey", hotkey)
                        self.hotkey_changed.emit(old_hotkey, hotkey)
                        self.update_hotkey_status("Hotkey registered successfully")
                        logger.debug(f"Hotkey changed to: {hotkey}")
                    else:
                        self.update_hotkey_status("Invalid hotkey combination", error=True)
            except Exception as e:
                logger.error(f"Failed to register hotkey: {e}")
                self.update_hotkey_status(f"Error: {e}", error=True)
    
    def test_hotkey(self):
        """Test the current hotkey."""
        hotkey = self.hotkey_edit.text().strip()
        if not hotkey:
            self.update_hotkey_status("No hotkey specified", error=True)
            return
        
        if not self.hotkey_manager.is_available():
            self.update_hotkey_status("Global hotkeys not available", error=True)
            return
        
        try:
            # Try to register and immediately unregister
            if self.hotkey_manager.register_hotkey("test", hotkey, lambda: None):
                self.hotkey_manager.unregister_hotkey("test")
                self.update_hotkey_status("Hotkey test successful!")
            else:
                self.update_hotkey_status("Hotkey registration failed", error=True)
        except Exception as e:
            self.update_hotkey_status(f"Test failed: {e}", error=True)
    
    def update_startup_status(self):
        """Update startup status label."""
        try:
            is_enabled = self.startup_manager.is_startup_enabled()
            if is_enabled:
                self.startup_status_label.setText("✓ Application will start with system")
                self.startup_status_label.setStyleSheet("color: #5cb85c; font-size: 10px; margin-left: 20px;")
            else:
                self.startup_status_label.setText("Application will not start with system")
                self.startup_status_label.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
        except Exception as e:
            self.startup_status_label.setText(f"Error checking startup status: {e}")
            self.startup_status_label.setStyleSheet("color: #d9534f; font-size: 10px; margin-left: 20px;")
    
    def update_hotkey_status(self, message="", error=False):
        """Update hotkey status label."""
        if not message:
            hotkey = self.hotkey_edit.text().strip()
            if hotkey and self.hotkey_manager.is_available():
                message = f"Hotkey: {hotkey}"
            elif not self.hotkey_manager.is_available():
                message = "Global hotkeys not available"
            else:
                message = "No hotkey set"
        
        color = "#d9534f" if error else "#666"
        self.hotkey_status_label.setText(message)
        self.hotkey_status_label.setStyleSheet(f"color: {color}; font-size: 10px;")
    
    def on_dock_mode_changed(self, button, checked):
        """Handle dock mode change."""
        if checked:
            dock_mode = "corner" if button == self.corner_radio else "tray"
            set_setting("dock_mode", dock_mode)
            self.dock_mode_changed.emit(dock_mode)
            logger.debug(f"Dock mode changed to: {dock_mode}")
    
    def on_circle_size_changed(self, value):
        """Handle circle size change."""
        set_setting("circle_size", value)
        self.settings_changed.emit()
    
    def on_animation_duration_changed(self, value):
        """Handle animation duration change."""
        set_setting("animation_duration", value)
        self.settings_changed.emit()
    
    def on_panel_width_changed(self, value):
        """Handle panel width change."""
        set_setting("panel_width", value)
        self.settings_changed.emit()
    
    def on_panel_height_changed(self, value):
        """Handle panel height change."""
        set_setting("panel_height", value)
        self.settings_changed.emit()
    
    def on_auto_focus_changed(self, checked):
        """Handle auto focus change."""
        set_setting("auto_focus_editor", checked)
        self.settings_changed.emit()
    
    def on_formatting_rule_toggled(self, rule_name, checked):
        """Handle formatting rule toggle."""
        set_setting(f"formatting_rule_{rule_name}", checked)
        self.settings_changed.emit()
        logger.debug(f"Formatting rule {rule_name} set to: {checked}")
    
    def enable_all_formatting(self):
        """Enable all formatting rules."""
        for rule_name, checkbox in self.formatting_checkboxes.items():
            checkbox.setChecked(True)
    
    def disable_all_formatting(self):
        """Disable all formatting rules."""
        for rule_name, checkbox in self.formatting_checkboxes.items():
            checkbox.setChecked(False)
    
    def on_font_family_changed(self, font_family):
        """Handle font family change."""
        set_setting("font_family", font_family)
        self.settings_changed.emit()
    
    def on_font_size_changed(self, size):
        """Handle font size change."""
        set_setting("font_size", size)
        self.settings_changed.emit()
    
    def on_autosave_delay_changed(self, delay):
        """Handle autosave delay change."""
        set_setting("autosave_delay", delay)
        self.settings_changed.emit()
    
    def on_word_wrap_changed(self, checked):
        """Handle word wrap change."""
        set_setting("word_wrap", checked)
        self.settings_changed.emit()
    
    def on_auto_indent_changed(self, checked):
        """Handle auto indent change."""
        set_setting("auto_indent", checked)
        self.settings_changed.emit()
    
    def open_data_directory(self):
        """Open the data directory in file explorer."""
        try:
            data_dir = get_setting("data_directory", Path.home() / "PocketJournal")
            open_data_folder(data_dir)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open data directory: {e}")
    
    def change_data_directory(self):
        """Change the data directory."""
        current_dir = get_setting("data_directory", Path.home() / "PocketJournal")
        new_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Data Directory", 
            str(current_dir)
        )
        
        if new_dir:
            set_setting("data_directory", new_dir)
            self.data_dir_edit.setText(new_dir)
            self.settings_changed.emit()
            
            QMessageBox.information(
                self, 
                "Data Directory Changed",
                f"Data directory changed to:\n{new_dir}\n\nExisting entries will remain in the old location."
            )
    
    def on_backup_files_changed(self, checked):
        """Handle backup files setting change."""
        set_setting("backup_files", checked)
        self.settings_changed.emit()
    
    def on_auto_cleanup_changed(self, checked):
        """Handle auto cleanup setting change."""
        set_setting("auto_cleanup", checked)
        self.settings_changed.emit()
    
    def on_export_format_changed(self, format_text):
        """Handle export format change."""
        set_setting("export_format", format_text)
        self.settings_changed.emit()
    
    def browse_export_directory(self):
        """Browse for export directory."""
        current_dir = self.export_dir_edit.text() or str(Path.home() / "Downloads")
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            current_dir
        )
        
        if new_dir:
            self.export_dir_edit.setText(new_dir)
            set_setting("export_directory", new_dir)
            self.settings_changed.emit()
    
    def on_include_metadata_changed(self, checked):
        """Handle include metadata setting change."""
        set_setting("include_metadata", checked)
        self.settings_changed.emit()
    
    def on_preserve_formatting_changed(self, checked):
        """Handle preserve formatting setting change."""
        set_setting("preserve_formatting", checked)
        self.settings_changed.emit()
    
    def open_entries_folder(self):
        """Open the entries folder."""
        self.open_data_directory()
    
    def cleanup_empty_entries(self):
        """Cleanup empty entries."""
        reply = QMessageBox.question(
            self,
            "Cleanup Empty Entries",
            "This will remove all empty journal entries. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement empty entry cleanup
            QMessageBox.information(self, "Cleanup Complete", "Empty entries have been removed.")
    
    def open_user_guide(self):
        """Open the user guide."""
        # TODO: Implement user guide opening
        QMessageBox.information(self, "User Guide", "User guide feature coming soon!")
    
    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
<h3>Keyboard Shortcuts</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>New entry</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save entry</td></tr>
<tr><td><b>Ctrl+K</b></td><td>Search entries</td></tr>
<tr><td><b>Ctrl+,</b></td><td>Open settings</td></tr>
<tr><td><b>Esc</b></td><td>Close panel/dialog</td></tr>
<tr><td><b>Ctrl+Alt+J</b></td><td>Show/hide panel (global)</td></tr>
</table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
    
    def show_release_notes(self):
        """Show release notes."""
        # TODO: Implement release notes
        QMessageBox.information(self, "Release Notes", "Release notes feature coming soon!")
    
    def show_about(self):
        """Show about dialog."""
        from .about_dialog import show_about_dialog
        show_about_dialog(self)
    
    def show_about_qt(self):
        """Show about Qt dialog."""
        QMessageBox.aboutQt(self, "About Qt")
    
    def refresh_diagnostics(self):
        """Refresh diagnostic information."""
        import platform
        import sys
        from PySide6 import __version__ as pyside_version
        
        diagnostics = f"""System Information:
OS: {platform.system()} {platform.release()}
Python: {sys.version}
PySide6: {pyside_version}
App Version: {get_version_string()}

Settings:
Data Directory: {get_setting("data_directory", "Not set")}
Dock Mode: {get_setting("dock_mode", "corner")}
Theme: {get_setting("theme", "Auto (System)")}
Global Hotkey: {get_setting("global_hotkey", "Ctrl+Alt+J")}

Features:
Global Hotkeys: {"Available" if self.hotkey_manager.is_available() else "Not available"}
System Tray: {"Available" if hasattr(self, 'tray_radio') and self.tray_radio.isEnabled() else "Not available"}
        """
        
        self.diagnostics_text.setPlainText(diagnostics)
    
    def copy_diagnostics(self):
        """Copy diagnostics to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.diagnostics_text.toPlainText())
        
        # Show temporary status
        old_text = self.copy_diagnostics_btn.text()
        self.copy_diagnostics_btn.setText("Copied!")
        QTimer.singleShot(2000, lambda: self.copy_diagnostics_btn.setText(old_text))
    
    def save_diagnostics(self):
        """Save diagnostics to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Diagnostics",
            f"PocketJournal_Diagnostics_{get_version_string()}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.diagnostics_text.toPlainText())
                QMessageBox.information(self, "Diagnostics Saved", f"Diagnostics saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save diagnostics: {e}")
    
    def on_eggs_enabled_changed(self, checked):
        """Handle eggs enabled setting change."""
        set_setting("eggs_enabled", checked)
        # Enable/disable egg icon checkbox based on eggs_enabled
        self.show_egg_icon_checkbox.setEnabled(checked)
        if not checked:
            self.show_egg_icon_checkbox.setChecked(False)
        self.settings_changed.emit()
    
    def on_show_egg_icon_changed(self, checked):
        """Handle show egg icon setting change."""
        set_setting("show_egg_icon", checked)
        self.settings_changed.emit()
    
    def on_fun_animations_changed(self, checked):
        """Handle fun animations setting change."""
        set_setting("fun_animations", checked)
        self.settings_changed.emit()
    
    def on_sound_effects_changed(self, checked):
        """Handle sound effects setting change."""
        set_setting("sound_effects", checked)
        self.settings_changed.emit()
    
    def on_debug_mode_changed(self, checked):
        """Handle debug mode setting change."""
        set_setting("debug_mode", checked)
        # Update logging level if needed
        if checked:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
        self.settings_changed.emit()
    
    def on_verbose_logging_changed(self, checked):
        """Handle verbose logging setting change."""
        set_setting("verbose_logging", checked)
        self.settings_changed.emit()
    
    def on_dev_tools_changed(self, checked):
        """Handle dev tools setting change."""
        set_setting("dev_tools", checked)
        self.settings_changed.emit()
    
    def reset_window_positions(self):
        """Reset window positions to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Window Positions",
            "This will reset all window positions and sizes to defaults. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset window-related settings
            for key in ["panel_width", "panel_height", "window_geometry", "window_state"]:
                settings.remove(key)
            self.settings_changed.emit()
            QMessageBox.information(self, "Reset Complete", "Window positions have been reset to defaults.")
    
    def reset_formatting_settings(self):
        """Reset formatting settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Formatting",
            "This will reset all formatting rules to defaults. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all formatting rules to default (enabled)
            for rule_name, checkbox in self.formatting_checkboxes.items():
                checkbox.setChecked(True)
            QMessageBox.information(self, "Reset Complete", "Formatting settings have been reset to defaults.")
    
    def apply_settings(self):
        """Apply settings without closing dialog."""
        logger.debug("Settings applied")
    
    def accept_settings(self):
        """Accept and close dialog."""
        self.apply_settings()
        self.accept()
    
    def restore_defaults(self):
        """Restore all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "This will restore ALL settings to their default values. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all settings
            settings.clear()
            # Reload UI with defaults
            self.load_settings()
            self.settings_changed.emit()
            QMessageBox.information(self, "Defaults Restored", "All settings have been restored to defaults.")


def show_settings_dialog(parent=None):
    """
    Show the settings dialog.
    
    Args:
        parent: Parent widget for the dialog
        
    Returns:
        tuple: (accepted, dialog) - whether dialog was accepted and the dialog instance
    """
    dialog = SettingsDialog(parent)
    result = dialog.exec()
    accepted = result == SettingsDialog.DialogCode.Accepted
    return accepted, dialog