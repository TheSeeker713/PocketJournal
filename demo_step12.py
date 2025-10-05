#!/usr/bin/env python3
"""
Demo for Step 12: About Dialog

Tests the About dialog functionality including:
- App name, version, build date display from version.json
- Data location display with working "Open" buttons  
- Mini changelog from about/changelog.md
- Access from both Help footer and Settings
- Credits dialog
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set up logging
import logging
logging.basicConfig(level=logging.DEBUG)

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

# Import our modules
from pocket_journal.ui.about_dialog import show_about_dialog
from pocket_journal.ui.settings_dialog import show_settings_dialog
from pocket_journal.ui.help_center import show_help_center
from pocket_journal.app_meta import APP_NAME, VERSION, BUILD_DATE, CHANNEL


class Step12DemoWindow(QMainWindow):
    """Demo window for testing Step 12 About dialog functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Step 12 Demo: About Dialog - {APP_NAME}")
        self.setGeometry(200, 200, 500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the demo interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Step 12: About Dialog Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "This demo tests the About dialog functionality:\n\n"
            "✓ Compact About modal sourced from version.json and app_meta\n"
            "✓ App name, version, build date, copyright, credits\n"
            "✓ Data locations with working 'Open' buttons\n"
            "✓ Mini changelog from about/changelog.md\n"
            "✓ Access from both Help footer and Settings"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; line-height: 1.4;")
        layout.addWidget(description)
        
        # Current version info
        version_info = QLabel(
            f"Current App Info:\n"
            f"• Name: {APP_NAME}\n"
            f"• Version: {VERSION}\n"
            f"• Build Date: {BUILD_DATE}\n"
            f"• Channel: {CHANNEL}"
        )
        version_info.setStyleSheet(
            "background-color: #f0f8ff; "
            "padding: 15px; "
            "border-radius: 5px; "
            "font-family: monospace;"
        )
        layout.addWidget(version_info)
        
        # Test buttons
        layout.addWidget(QLabel("Test About Dialog Access:"))
        
        # Direct about dialog
        self.about_btn = QPushButton("🔍 Show About Dialog (Direct)")
        self.about_btn.setMinimumHeight(40)
        self.about_btn.clicked.connect(self.show_about_direct)
        layout.addWidget(self.about_btn)
        
        # About from Settings
        self.settings_btn = QPushButton("⚙️ Open Settings → Help & Support → About")
        self.settings_btn.setMinimumHeight(40)
        self.settings_btn.clicked.connect(self.show_settings_about)
        layout.addWidget(self.settings_btn)
        
        # About from Help Center
        self.help_btn = QPushButton("❓ Open Help Center → About (footer)")
        self.help_btn.setMinimumHeight(40)
        self.help_btn.clicked.connect(self.show_help_about)
        layout.addWidget(self.help_btn)
        
        layout.addStretch()
        
        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Test direct About dialog\n"
            "2. Verify version info matches above\n"
            "3. Test 'Open' buttons for data locations\n"
            "4. Check changelog content\n"
            "5. Test Credits dialog\n"
            "6. Test access from Settings and Help Center"
        )
        instructions.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(instructions)
    
    def show_about_direct(self):
        """Show about dialog directly."""
        print("\\n" + "="*50)
        print("Testing Direct About Dialog")
        print("="*50)
        show_about_dialog(self)
    
    def show_settings_about(self):
        """Show settings dialog for about testing."""
        print("\\n" + "="*50)
        print("Testing About from Settings")
        print("="*50)
        print("1. Opening Settings...")
        print("2. Navigate to 'Help & Support' tab")
        print("3. Click 'About' button")
        show_settings_dialog(self)
    
    def show_help_about(self):
        """Show help center for about testing."""
        print("\\n" + "="*50)
        print("Testing About from Help Center")
        print("="*50)
        print("1. Opening Help Center...")
        print("2. Look for 'About' button in footer")
        print("3. Click 'About' button")
        show_help_center(self)


def run_step12_demo():
    """Run the Step 12 demo."""
    print("="*60)
    print("STEP 12 DEMO: About Dialog")
    print("="*60)
    print()
    print("Testing About dialog functionality:")
    print("• Compact modal with app info from version.json")
    print("• Data locations with working Open buttons")
    print("• Mini changelog from about/changelog.md")
    print("• Access from Help footer and Settings")
    print("• Credits and acknowledgments")
    print()
    print("Demo will open a test window with access buttons...")
    print()
    
    app = QApplication(sys.argv)
    
    # Create and show demo window
    demo_window = Step12DemoWindow()
    demo_window.show()
    
    print("Demo window opened! Test the About dialog functionality.")
    print("\\nExpected behaviors:")
    print("✓ About dialog shows app name, version, build date")
    print("✓ Version info matches version.json")
    print("✓ Data location 'Open' buttons work")
    print("✓ Changelog shows latest 3 entries")
    print("✓ Credits dialog opens with acknowledgments")
    print("✓ About accessible from Settings Help & Support tab")
    print("✓ About accessible from Help Center footer")
    
    return app.exec()


if __name__ == "__main__":
    run_step12_demo()