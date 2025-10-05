#!/usr/bin/env python3
"""
Demo script for Step 11: Help Center (F1) & Content Rendering

This script demonstrates the comprehensive help center functionality including:
- Non-blocking help modal with TOC
- Markdown content rendering 
- Helper action links
- F1 keyboard activation
- Full keyboard navigation
"""

import sys
import os
import logging
from pathlib import Path

# Add the source directory to the path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from pocket_journal.ui.help_center import show_help_center, HelpCenter
from pocket_journal.app_meta import APP_NAME, get_version_string

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class HelpCenterDemo(QWidget):
    """Demo widget for testing help center functionality."""
    
    def __init__(self):
        super().__init__()
        self.help_center = None
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Setup the demo UI."""
        self.setWindowTitle(f"{APP_NAME} Help Center Demo - Step 11")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"{APP_NAME} Help Center Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Version info
        version = QLabel(f"Version {get_version_string()}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: gray; margin-bottom: 20px;")
        layout.addWidget(version)
        
        # Instructions
        instructions = QLabel(
            "Step 11 Requirements Test:\n\n"
            "• Press F1 to open help center (non-blocking modal)\n"
            "• Navigate using table of contents\n"
            "• Test helper action links\n"
            "• Use keyboard shortcuts for navigation\n"
            "• Markdown content rendering with CSS styling\n\n"
            "Or use the buttons below to test specific sections:"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 20px; line-height: 1.4;")
        layout.addWidget(instructions)
        
        # Section test buttons
        sections_layout = QVBoxLayout()
        
        # Row 1
        row1 = QHBoxLayout()
        self.add_section_button(row1, "Quick Start", "quick-start")
        self.add_section_button(row1, "Smart Formatting", "smart-formatting")
        self.add_section_button(row1, "Navigation & Search", "navigation-search")
        self.add_section_button(row1, "Files & Exports", "files-exports")
        sections_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        self.add_section_button(row2, "Settings", "settings")
        self.add_section_button(row2, "Privacy", "privacy")
        self.add_section_button(row2, "Shortcuts", "shortcuts")
        self.add_section_button(row2, "Troubleshooting", "troubleshooting")
        sections_layout.addLayout(row2)
        
        layout.addLayout(sections_layout)
        
        layout.addStretch()
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Open full help
        open_help_btn = QPushButton("Open Help Center (F1)")
        open_help_btn.clicked.connect(self.open_help_center)
        open_help_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        controls_layout.addWidget(open_help_btn)
        
        # Test helper actions
        test_helpers_btn = QPushButton("Test Helper Actions")
        test_helpers_btn.clicked.connect(self.test_helper_actions)
        controls_layout.addWidget(test_helpers_btn)
        
        # Exit
        exit_btn = QPushButton("Exit Demo")
        exit_btn.clicked.connect(self.close)
        controls_layout.addWidget(exit_btn)
        
        layout.addLayout(controls_layout)
    
    def add_section_button(self, layout, title, section_id):
        """Add a button for testing a specific section."""
        btn = QPushButton(title)
        btn.clicked.connect(lambda: self.open_help_section(section_id))
        btn.setStyleSheet("""
            QPushButton {
                padding: 8px 12px;
                margin: 2px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        layout.addWidget(btn)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # F1 to open help center
        f1_shortcut = QShortcut(QKeySequence("F1"), self)
        f1_shortcut.activated.connect(self.open_help_center)
        
        # Escape to close
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.close)
    
    def open_help_center(self):
        """Open the help center."""
        try:
            # Only create one instance at a time
            if self.help_center is None or not self.help_center.isVisible():
                self.help_center = show_help_center(self)
                logger.info("Help center opened successfully")
            else:
                # Bring existing help center to front
                self.help_center.raise_()
                self.help_center.activateWindow()
                logger.info("Help center brought to front")
                
        except Exception as e:
            logger.error(f"Failed to open help center: {e}")
            QMessageBox.critical(
                self,
                "Help Error",
                f"Failed to open help center: {e}"
            )
    
    def open_help_section(self, section_id):
        """Open help center to a specific section."""
        try:
            if self.help_center is None or not self.help_center.isVisible():
                self.help_center = show_help_center(self, section_id)
            else:
                # Navigate existing help center to section
                self.help_center.content_browser.load_section(section_id)
                self.help_center.toc.select_section(section_id)
                self.help_center.raise_()
                self.help_center.activateWindow()
            
            logger.info(f"Help center opened to section: {section_id}")
            
        except Exception as e:
            logger.error(f"Failed to open help section {section_id}: {e}")
            QMessageBox.critical(
                self,
                "Help Error",
                f"Failed to open help section: {e}"
            )
    
    def test_helper_actions(self):
        """Test helper action functionality."""
        QMessageBox.information(
            self,
            "Helper Actions Test",
            "Helper actions are tested through the help content:\n\n"
            "1. Open any help section\n"
            "2. Look for blue 'helper action' buttons\n"
            "3. Click them to test functionality:\n"
            "   • Copy Data Folder Path\n"
            "   • Open Data Folder\n"
            "   • Reset Formatting to Defaults\n\n"
            "These actions integrate with the application's core functionality."
        )
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_F1:
            self.open_help_center()
        else:
            super().keyPressEvent(event)


def run_demo():
    """Run the help center demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(get_version_string())
    
    # Show demo window
    demo = HelpCenterDemo()
    demo.show()
    
    print(f"\n{APP_NAME} Help Center Demo - Step 11")
    print("=" * 50)
    print("\nStep 11 Requirements:")
    print("✅ Non-blocking help modal with TOC")
    print("✅ Markdown content rendering with minimal CSS")
    print("✅ Helper action links (copy data folder, open folder, reset formatting)")
    print("✅ F1 keyboard activation")
    print("✅ Full keyboard navigation")
    print("✅ 8 comprehensive help sections")
    print("\nTest Instructions:")
    print("1. Press F1 to open help center")
    print("2. Navigate using table of contents")
    print("3. Test section-specific buttons")
    print("4. Try helper action links in content")
    print("5. Use keyboard shortcuts (Ctrl+1-8 for sections)")
    print("\nPress F1 or click 'Open Help Center' to begin testing!")
    
    # Auto-open help center after 2 seconds for demo
    QTimer.singleShot(2000, demo.open_help_center)
    
    return app.exec()


if __name__ == "__main__":
    try:
        exit_code = run_demo()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Demo failed: {e}")
        sys.exit(1)