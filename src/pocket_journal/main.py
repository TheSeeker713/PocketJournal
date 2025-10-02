"""
Main application entry point for PocketJournal.

This module contains the main application class and entry point function.
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QMenuBar, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction

from .app_meta import APP_NAME, ORG_NAME, VERSION, get_app_title, get_version_string
from .settings import settings, get_setting, set_setting
from .ui.launcher_manager import LauncherManager
from .ui.settings_dialog import show_settings_dialog

logger = logging.getLogger(__name__)


class PocketJournalMainWindow(QMainWindow):
    """Main window for the PocketJournal application."""
    
    def __init__(self):
        super().__init__()
        self.launcher_manager = None
        self.init_ui()
        self.setup_launcher()
        self.setup_menu()
    
    def setup_launcher(self):
        """Setup the micro-launcher system."""
        self.launcher_manager = LauncherManager(self)
        
        # Connect launcher signals
        self.launcher_manager.panel_expanded.connect(self.on_panel_expanded)
        self.launcher_manager.panel_collapsed.connect(self.on_panel_collapsed)
        self.launcher_manager.dock_mode_changed.connect(self.on_dock_mode_changed)
        
        # Connect tray signals (if in tray mode)
        if hasattr(self.launcher_manager, 'system_tray') and self.launcher_manager.system_tray:
            self.launcher_manager.system_tray.show_window_requested.connect(self.show_and_raise)
            self.launcher_manager.system_tray.settings_requested.connect(self.show_settings)
            self.launcher_manager.system_tray.exit_requested.connect(self.close_application)
    
    def on_panel_expanded(self):
        """Handle when the editor panel is expanded."""
        # Optionally minimize or hide the main window when panel is active
        if get_setting("minimize_main_when_panel_open", False):
            self.showMinimized()
    
    def on_panel_collapsed(self):
        """Handle when the editor panel is collapsed."""
        # Restore main window if it was minimized
        if self.isMinimized():
            self.showNormal()
            self.raise_()
            self.activateWindow()
    
    def on_dock_mode_changed(self, new_mode: str):
        """Handle when dock mode changes."""
        logger.info(f"Dock mode changed to: {new_mode}")
        # Reconnect tray signals if switching to tray mode
        if new_mode == "tray" and hasattr(self.launcher_manager, 'system_tray') and self.launcher_manager.system_tray:
            self.launcher_manager.system_tray.show_window_requested.connect(self.show_and_raise)
            self.launcher_manager.system_tray.settings_requested.connect(self.show_settings)
            self.launcher_manager.system_tray.exit_requested.connect(self.close_application)
    
    def show_and_raise(self):
        """Show and raise the main window (for tray mode)."""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = show_settings_dialog(self)
        if dialog:
            # Handle settings changes
            dialog.dock_mode_changed.connect(self.handle_dock_mode_change)
    
    def handle_dock_mode_change(self, new_mode: str):
        """Handle dock mode change from settings."""
        current_mode = get_setting("dock_mode", "corner")
        if new_mode != current_mode:
            # Show restart message
            QMessageBox.information(
                self, 
                "Restart Required",
                f"Dock mode has been changed to '{new_mode}'.\n"
                "Please restart the application for the change to take effect."
            )
    
    def close_application(self):
        """Close the application properly."""
        self.close()
    
    def setup_menu(self):
        """Setup the main menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        quick_jot_action = QAction("&Quick Jot", self)
        quick_jot_action.setShortcut("Ctrl+J")
        quick_jot_action.triggered.connect(self.open_quick_jot)
        file_menu.addAction(quick_jot_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_quick_jot(self):
        """Open the quick jot panel."""
        if self.launcher_manager:
            self.launcher_manager.expand_panel()
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME}</h3>"
            f"<p>Version {get_version_string()}</p>"
            f"<p>A simple journaling application with a micro-launcher interface.</p>"
            f"<p>© 2024 {ORG_NAME}</p>"
        )
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window title using app metadata
        self.setWindowTitle(get_app_title())
        
        # Load window geometry from settings
        geometry = get_setting("window_geometry", {})
        width = geometry.get("width", 800)
        height = geometry.get("height", 600)
        self.resize(width, height)
        
        # Set minimum size
        self.setMinimumSize(600, 400)
        
        # Position window if coordinates are saved
        x = geometry.get("x")
        y = geometry.get("y")
        if x is not None and y is not None:
            self.move(x, y)
        
        # Create central widget with placeholder content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add welcome content with app info
        welcome_label = QLabel(f"Welcome to {APP_NAME}!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 30px;
            }
        """)
        
        version_label = QLabel(f"Version {get_version_string()}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #95a5a6;
                margin-bottom: 10px;
            }
        """)
        
        subtitle_label = QLabel("Your personal journaling companion")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        
        # Settings info for development
        settings_info = QLabel(f"Settings: {settings.settings_file}\nData: {settings.data_dir}\n\nMicro-launcher active! Look for the blue circle in the corner.\nClick it to expand the quick editor.")
        settings_info.setAlignment(Qt.AlignCenter)
        settings_info.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #bdc3c7;
                font-family: 'Consolas', 'Courier New', monospace;
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                line-height: 1.4;
            }
        """)
        
        layout.addWidget(welcome_label)
        layout.addWidget(version_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(settings_info)
        
        # Set window icon (placeholder path)
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def closeEvent(self, event):
        """Handle window close event to save settings."""
        # Save window geometry
        geometry = self.geometry()
        settings.set("window_geometry.width", geometry.width())
        settings.set("window_geometry.height", geometry.height())
        settings.set("window_geometry.x", geometry.x())
        settings.set("window_geometry.y", geometry.y())
        
        # Shutdown launcher manager
        if self.launcher_manager:
            self.launcher_manager.shutdown()
        
        # Accept the close event
        event.accept()


class PocketJournalApp:
    """Main application class for PocketJournal."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up application logging."""
        log_dir = settings.get_log_directory()
        log_file = log_dir / "pocket_journal.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Log startup info
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {APP_NAME} v{VERSION}")
        logger.info(f"Settings file: {settings.settings_file}")
        logger.info(f"Data directory: {settings.data_dir}")
    
    def run(self):
        """Run the application."""
        # Create QApplication instance
        self.app = QApplication(sys.argv)
        
        # Set application properties using app metadata
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(VERSION)
        self.app.setOrganizationName(ORG_NAME)
        
        # Log application info
        logger = logging.getLogger(__name__)
        logger.info(f"Qt Application initialized")
        logger.info(f"Settings loaded: theme={get_setting('theme')}, hotkey={get_setting('hotkey')}")
        
        # Create and show main window
        self.main_window = PocketJournalMainWindow()
        self.main_window.show()
        
        # Log window creation
        logger.info("Main window created and shown")
        
        # Start event loop
        exit_code = self.app.exec()
        logger.info(f"Application exiting with code {exit_code}")
        return exit_code


def main():
    """Main entry point for the application."""
    try:
        app = PocketJournalApp()
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()