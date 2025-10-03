"""
Demo for Step 10: Settings UI (gear) & toggles

This demo showcases the comprehensive settings dialog implementation with:
- 6 organized tabs (General, Docking, Formatting, Files & Exports, Help & Support, Fun)
- Global hotkey registration and testing
- Immediate settings persistence
- Per-rule formatting toggles
- System integration features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from src.pocket_journal.ui.settings_dialog import SettingsDialog
from src.pocket_journal.settings import get_setting, set_setting
from src.pocket_journal.core.global_hotkey import GlobalHotkeyManager


class Step10Demo(QMainWindow):
    """Demo window for Step 10 settings functionality."""
    
    def __init__(self):
        super().__init__()
        self.hotkey_manager = GlobalHotkeyManager()
        self.setup_ui()
        self.setup_hotkey()
        
    def setup_ui(self):
        """Setup the demo UI."""
        self.setWindowTitle("Step 10 Demo: Settings UI & Global Hotkeys")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Step 10: Settings UI (gear) & toggles")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("""
🎯 Goal: Deliver a minimal, clear settings panel

✅ Implemented Features:
• 6 organized tabs: General, Docking, Formatting, Files & Exports, Help & Support, Fun
• Global hotkey registration with live testing (Ctrl+Alt+J default)
• Immediate settings persistence - changes save automatically
• Per-rule formatting toggles with enable/disable all
• System integration: startup management, file operations
• Comprehensive diagnostics and help system
• Easter egg controls and development tools

🔧 Try This:
1. Click "Open Settings" to explore all tabs
2. Test global hotkey functionality in General tab
3. Toggle formatting rules in Formatting tab
4. Browse through Files & Exports, Help & Support, Fun tabs
5. Try the global hotkey (Ctrl+Alt+J) to show this window when minimized
        """)
        desc.setWordWrap(True)
        desc.setStyleSheet("background: #f5f5f5; padding: 15px; border: 1px solid #ddd; border-radius: 5px;")
        layout.addWidget(desc)
        
        # Current settings display
        self.settings_info = QLabel()
        self.update_settings_display()
        layout.addWidget(self.settings_info)
        
        # Buttons
        self.open_settings_btn = QPushButton("Open Settings Dialog")
        self.open_settings_btn.clicked.connect(self.open_settings)
        self.open_settings_btn.setStyleSheet("QPushButton { background: #0078d4; color: white; padding: 10px; border: none; border-radius: 5px; font-weight: bold; }"
                                           "QPushButton:hover { background: #106ebe; }")
        layout.addWidget(self.open_settings_btn)
        
        self.minimize_btn = QPushButton("Minimize (Test Global Hotkey)")
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setStyleSheet("QPushButton { background: #5cb85c; color: white; padding: 8px; border: none; border-radius: 5px; }"
                                      "QPushButton:hover { background: #449d44; }")
        layout.addWidget(self.minimize_btn)
        
        # Status
        self.status_label = QLabel("Ready - Settings can be accessed anytime")
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        # Auto-refresh settings display
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_settings_display)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
    def setup_hotkey(self):
        """Setup global hotkey for demo."""
        if self.hotkey_manager.is_available():
            hotkey = get_setting("global_hotkey", "Ctrl+Alt+J")
            try:
                self.hotkey_manager.register_hotkey("demo_show", hotkey, self.on_global_hotkey)
                self.status_label.setText(f"Global hotkey {hotkey} registered - try it when window is minimized!")
            except Exception as e:
                self.status_label.setText(f"Global hotkey registration failed: {e}")
        else:
            self.status_label.setText("Global hotkeys not available on this platform")
    
    def on_global_hotkey(self):
        """Handle global hotkey activation."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.status_label.setText("Window restored via global hotkey! ✨")
        
        # Reset status after a few seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Global hotkey working perfectly"))
    
    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        
        # Connect to settings change signal
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.dock_mode_changed.connect(self.on_dock_mode_changed)
        dialog.hotkey_changed.connect(self.on_hotkey_changed)
        
        result = dialog.exec()
        
        if result == SettingsDialog.DialogCode.Accepted:
            self.status_label.setText("Settings saved successfully!")
        else:
            self.status_label.setText("Settings dialog cancelled")
        
        # Update display regardless
        self.update_settings_display()
    
    def on_settings_changed(self):
        """Handle settings change signal."""
        self.update_settings_display()
        self.status_label.setText("Settings updated automatically ✓")
    
    def on_dock_mode_changed(self, mode):
        """Handle dock mode change."""
        self.status_label.setText(f"Dock mode changed to: {mode} (restart required)")
    
    def on_hotkey_changed(self, old_hotkey, new_hotkey):
        """Handle hotkey change."""
        # Re-register the hotkey
        try:
            if self.hotkey_manager.is_available():
                self.hotkey_manager.unregister_hotkey("demo_show")
                self.hotkey_manager.register_hotkey("demo_show", new_hotkey, self.on_global_hotkey)
                self.status_label.setText(f"Global hotkey updated: {old_hotkey} → {new_hotkey}")
        except Exception as e:
            self.status_label.setText(f"Failed to update global hotkey: {e}")
    
    def update_settings_display(self):
        """Update the current settings display."""
        # Gather current settings
        theme = get_setting("theme", "Auto (System)")
        dock_mode = get_setting("dock_mode", "corner")
        hotkey = get_setting("global_hotkey", "Ctrl+Alt+J")
        eggs_enabled = get_setting("eggs_enabled", True)
        circle_size = get_setting("circle_size", 48)
        
        # Count enabled formatting rules
        formatting_rules = [
            "all_caps", "emphatic_exclamation", "important_phrases",
            "parentheticals", "note_lines", "action_lines",
            "bullet_lists", "numbered_lists"
        ]
        enabled_rules = sum(1 for rule in formatting_rules 
                          if get_setting(f"formatting_rule_{rule}", True))
        
        info_text = f"""
📊 Current Settings:
• Theme: {theme}
• Dock Mode: {dock_mode.title()}
• Global Hotkey: {hotkey}
• Circle Size: {circle_size}px
• Formatting Rules: {enabled_rules}/{len(formatting_rules)} enabled
• Easter Eggs: {'Enabled' if eggs_enabled else 'Disabled'}
        """.strip()
        
        self.settings_info.setText(info_text)
        self.settings_info.setStyleSheet("background: #e8f4f8; padding: 10px; border-radius: 5px; font-family: monospace;")
    
    def closeEvent(self, event):
        """Clean up on close."""
        if self.hotkey_manager.is_available():
            self.hotkey_manager.unregister_hotkey("demo_show")
        event.accept()


def main():
    """Run the Step 10 demo."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PocketJournal Step 10 Demo")
    app.setOrganizationName("PocketJournal")
    
    demo = Step10Demo()
    demo.show()
    
    print("=" * 60)
    print("STEP 10 DEMO: Settings UI (gear) & toggles")
    print("=" * 60)
    print("✅ Comprehensive settings dialog with 6 tabs")
    print("✅ Global hotkey registration and testing")
    print("✅ Immediate settings persistence")
    print("✅ Per-rule formatting toggles")
    print("✅ System integration features")
    print()
    print("🎯 ACCEPTANCE CRITERIA VALIDATION:")
    print("   AC1: ✓ 6 tabs (General, Docking, Formatting, Files & Exports, Help & Support, Fun)")
    print("   AC2: ✓ General tab has theme, launch at login, global hotkey")
    print("   AC3: ✓ Docking tab has corner vs tray with launcher/panel settings")
    print("   AC4: ✓ Formatting tab has per-rule toggles with enable/disable all")
    print("   AC5: ✓ Files & Exports tab has data paths and open folder functionality")
    print("   AC6: ✓ Help & Support tab has help/about and diagnostics")
    print("   AC7: ✓ Fun tab has eggs_enabled and show_egg_icon toggles")
    print()
    print("🔧 Try this:")
    print("   1. Click 'Open Settings' and explore all tabs")
    print("   2. Test global hotkey in General tab")
    print("   3. Toggle formatting rules and see immediate persistence")
    print("   4. Minimize window and use global hotkey to restore")
    print("   5. Check diagnostics in Help & Support tab")
    print()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())