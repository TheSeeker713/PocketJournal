"""
Main application entry point for PocketJournal.

This module contains the main application class and entry point function.
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .app_meta import APP_NAME, ORG_NAME, VERSION, get_app_title, get_version_string
from .settings import settings, get_setting


class PocketJournalMainWindow(QMainWindow):
    """Main window for the PocketJournal application."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
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
        settings_info = QLabel(f"Settings: {settings.settings_file}\nData: {settings.data_dir}")
        settings_info.setAlignment(Qt.AlignCenter)
        settings_info.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #bdc3c7;
                font-family: 'Consolas', 'Courier New', monospace;
                margin-top: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
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