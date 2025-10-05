"""
Main application entry point for PocketJournal.

This module contains the main application class and entry point function.
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QMessageBox, QPushButton, QLineEdit
)
from PySide6.QtGui import QIcon, QAction, QShortcut, QKeySequence

from .app_meta import APP_NAME, ORG_NAME, VERSION, get_app_title
from .settings import settings, get_setting
from .ui.launcher_manager import LauncherManager
from .ui.settings_dialog import show_settings_dialog
from .ui.help_center import show_help_center

logger = logging.getLogger(__name__)


class PocketJournalMainWindow(QMainWindow):
    """Main window for the PocketJournal application."""
    
    def __init__(self):
        super().__init__()
        self.launcher_manager = None
        self.help_center = None  # Store help center reference
        self.init_ui()
        self.setup_launcher()
        self.setup_menu()
        self.setup_global_shortcuts()
    
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
            self.launcher_manager.system_tray.about_requested.connect(self.show_about)
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
            self.launcher_manager.system_tray.about_requested.connect(self.show_about)
            self.launcher_manager.system_tray.exit_requested.connect(self.close_application)
    
    def show_and_raise(self):
        """Show and raise the main window (for tray mode)."""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def show_settings(self):
        """Show the settings dialog."""
        accepted, dialog = show_settings_dialog(self)
        if dialog:
            # Handle settings changes
            dialog.dock_mode_changed.connect(self.handle_dock_mode_change)
    
    def show_about(self):
        """Show the about dialog."""
        from .ui.about_dialog import show_about_dialog
        show_about_dialog(self)
    
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
        
        help_action = QAction("&Help Center", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help_center)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_global_shortcuts(self):
        """Setup global keyboard shortcuts."""
        # F1 for help - accessible from anywhere in the application
        f1_shortcut = QShortcut(QKeySequence("F1"), self)
        f1_shortcut.activated.connect(self.show_help_center)
        
        # Additional global shortcuts for launcher access
        if self.launcher_manager:
            # Ctrl+J for quick jot (already in menu, but ensure global access)
            quick_jot_shortcut = QShortcut(QKeySequence("Ctrl+J"), self)
            quick_jot_shortcut.activated.connect(self.open_quick_jot)
    
    def show_help_center(self, section=None):
        """Show the help center dialog."""
        try:
            # Only create one instance at a time
            if self.help_center is None or not self.help_center.isVisible():
                self.help_center = show_help_center(self, section)
            else:
                # Bring existing help center to front
                self.help_center.raise_()
                self.help_center.activateWindow()
                
                # Navigate to specific section if requested
                if section:
                    self.help_center.content_browser.load_section(section)
                    self.help_center.toc.select_section(section)
                    
        except Exception as e:
            logger.error(f"Failed to show help center: {e}")
            QMessageBox.critical(
                self,
                "Help Error",
                f"Failed to open help center: {e}"
            )
    
    def open_quick_jot(self):
        """Open the quick jot panel."""
        if self.launcher_manager:
            self.launcher_manager.expand_panel()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window title using app metadata
        self.setWindowTitle(get_app_title())
        
        # Load window geometry from settings
        geometry = get_setting("window_geometry", {})
        width = geometry.get("width", 900)
        height = geometry.get("height", 700)
        self.resize(width, height)
        
        # Set minimum size
        self.setMinimumSize(800, 600)
        
        # Position window if coordinates are saved
        x = geometry.get("x")
        y = geometry.get("y")
        if x is not None and y is not None:
            self.move(x, y)
        
        # Create main writing interface
        self.setup_writing_interface()
        
        # Set window icon (placeholder path)
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def setup_writing_interface(self):
        """Setup the main writing-focused interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Header section with date and minimal controls
        header = self.create_header_section()
        main_layout.addWidget(header)
        
        # Main writing area
        writing_area = self.create_writing_area()
        main_layout.addWidget(writing_area)
        
        # Bottom bar with controls
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)
        
        # Apply modern styling
        self.apply_modern_styling()
        
        # Initialize word count
        self.update_word_count()
    
    def create_header_section(self):
        """Create the header with date and minimal controls."""
        from datetime import datetime
        
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(52, 73, 94, 0.9), stop:1 rgba(44, 62, 80, 0.9));
                border-bottom: 2px solid rgba(52, 152, 219, 0.3);
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        header.setLayout(layout)
        
        # Date display
        today = datetime.now().strftime("%B %d, %Y")
        date_label = QLabel(today)
        date_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #ecf0f1;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(date_label)
        
        layout.addStretch()
        
        # Quick actions
        new_btn = QPushButton("New Entry")
        new_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
        new_btn.clicked.connect(self.new_entry)
        layout.addWidget(new_btn)
        
        return header
    
    def create_writing_area(self):
        """Create the main writing area."""
        from PySide6.QtWidgets import QTextEdit
        
        # Container for writing area
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        container.setLayout(layout)
        
        # Entry title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What's on your mind today?")
        self.title_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: 600;
                color: #ecf0f1;
                background: rgba(52, 73, 94, 0.6);
                border: none;
                border-bottom: 3px solid rgba(52, 152, 219, 0.5);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }
            QLineEdit:focus {
                border-bottom: 3px solid #3498db;
                background: rgba(52, 73, 94, 0.8);
                outline: none;
            }
        """)
        layout.addWidget(self.title_input)
        
        # Main text editor
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Take a moment to reflect...\n\nFor more thought-provoking questions and prompts, check out the Help menu.")
        self.text_editor.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                line-height: 1.6;
                color: #ecf0f1;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:0.5 #2c3e50, stop:1 #34495e);
                border: 2px solid rgba(52, 152, 219, 0.3);
                padding: 25px;
                border-radius: 12px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTextEdit:focus {
                outline: none;
                border: 2px solid #3498db;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:0.5 #34495e, stop:1 #2c3e50);
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 4px;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: rgba(52, 152, 219, 0.7);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(52, 152, 219, 0.9);
            }
        """)
        layout.addWidget(self.text_editor)
        
        # Set focus to text editor immediately
        self.text_editor.setFocus()
        
        # Connect word count update
        self.text_editor.textChanged.connect(self.update_word_count)
        
        return container
    
    def create_bottom_bar(self):
        """Create the bottom bar with controls."""
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(50)
        bottom_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(44, 62, 80, 0.9), stop:1 rgba(52, 73, 94, 0.9));
                border-top: 2px solid rgba(52, 152, 219, 0.3);
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        bottom_bar.setLayout(layout)
        
        # Word count
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: rgba(236, 240, 241, 0.7);
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.word_count_label)
        
        layout.addStretch()
        
        # Action buttons
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_entry)
        layout.addWidget(save_btn)
        
        return bottom_bar
    
    def apply_modern_styling(self):
        """Apply modern Windows 11-inspired styling with dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:0.5 #34495e, stop:1 #2c3e50);
                color: #ecf0f1;
            }
            QWidget {
                font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }
        """)
    
    def new_entry(self):
        """Create a new entry."""
        self.title_input.clear()
        self.text_editor.clear()
        self.title_input.setFocus()
    
    def save_entry(self):
        """Save the current entry."""
        title = self.title_input.text().strip()
        content = self.text_editor.toPlainText().strip()
        
        if not title and not content:
            return
        
        # For now, just show a message - implement actual saving later
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Saved", "Entry saved successfully!")
    
    def update_word_count(self):
        """Update the word count display."""
        content = self.text_editor.toPlainText()
        word_count = len(content.split()) if content.strip() else 0
        self.word_count_label.setText(f"{word_count} words")
    
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