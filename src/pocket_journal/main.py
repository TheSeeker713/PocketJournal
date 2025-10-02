"""
Main application entry point for PocketJournal.

This module contains the main application class and entry point function.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class PocketJournalMainWindow(QMainWindow):
    """Main window for the PocketJournal application."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PocketJournal")
        self.setMinimumSize(800, 600)
        
        # Create central widget with placeholder content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add placeholder content
        welcome_label = QLabel("Welcome to PocketJournal!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 50px;
            }
        """)
        
        subtitle_label = QLabel("Your personal journaling companion")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 50px;
            }
        """)
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        
        # Set window icon (placeholder path)
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))


class PocketJournalApp:
    """Main application class for PocketJournal."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def run(self):
        """Run the application."""
        # Create QApplication instance
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("PocketJournal")
        self.app.setApplicationVersion("0.1.0")
        self.app.setOrganizationName("PocketJournal Team")
        
        # Create and show main window
        self.main_window = PocketJournalMainWindow()
        self.main_window.show()
        
        # Start event loop
        return self.app.exec()


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