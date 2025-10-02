"""
System tray functionality for PocketJournal.

This module implements the system tray icon with context menu and
handles the dock mode switching between corner launcher and tray.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QApplication, QWidget, QMessageBox
)
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen, QAction

from ..settings import settings, get_setting, set_setting
from ..app_meta import APP_NAME, get_app_title, get_version_string

logger = logging.getLogger(__name__)


class SystemTrayManager(QObject):
    """
    Manages the system tray icon and its context menu.
    
    Provides an alternative interface to the micro-launcher when
    dock_mode is set to "tray".
    """
    
    # Signals
    quick_jot_requested = Signal()
    show_window_requested = Signal()
    settings_requested = Signal()
    about_requested = Signal()
    help_requested = Signal()
    exit_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tray_icon = None
        self.context_menu = None
        self.is_available = False
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available on this system")
            return
        
        self.is_available = True
        self._create_tray_icon()
        self._create_context_menu()
        self._setup_connections()
        
        logger.info("System tray manager initialized")
    
    def _create_tray_icon(self):
        """Create the system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create icon
        icon = self._create_tray_icon_image()
        self.tray_icon.setIcon(icon)
        
        # Set tooltip
        self.tray_icon.setToolTip(f"{APP_NAME} - Quick journaling")
        
        logger.debug("System tray icon created")
    
    def _create_tray_icon_image(self) -> QIcon:
        """Create the tray icon image."""
        # Create a simple book icon for the tray
        size = 16  # Standard tray icon size
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw book icon
        book_rect = pixmap.rect().adjusted(2, 2, -2, -2)
        
        # Book background
        painter.setBrush(QBrush(QColor(45, 140, 240)))  # Blue color
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawRect(book_rect)
        
        # Book pages
        page_x = book_rect.left() + 2
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawLine(page_x, book_rect.top(), page_x, book_rect.bottom())
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_context_menu(self):
        """Create the context menu for the tray icon."""
        self.context_menu = QMenu()
        
        # Quick Jot action
        quick_jot_action = QAction("Quick Jot", self)
        quick_jot_action.setToolTip("Open quick note editor")
        quick_jot_action.triggered.connect(self.quick_jot_requested.emit)
        self.context_menu.addAction(quick_jot_action)
        
        # Open Window action
        open_main_action = QAction("Open Window", self)
        open_main_action.setToolTip("Show the main application window")
        open_main_action.triggered.connect(self.show_window_requested.emit)
        self.context_menu.addAction(open_main_action)
        
        self.context_menu.addSeparator()
        
        # Recent submenu (placeholder for now)
        recent_menu = self.context_menu.addMenu("Recent")
        no_recent_action = QAction("No recent files", self)
        no_recent_action.setEnabled(False)
        recent_menu.addAction(no_recent_action)
        
        self.context_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setToolTip("Open application settings")
        settings_action.triggered.connect(self.settings_requested.emit)
        self.context_menu.addAction(settings_action)
        
        # Help action
        help_action = QAction("Help", self)
        help_action.setToolTip("Show help documentation")
        help_action.triggered.connect(self.help_requested.emit)
        self.context_menu.addAction(help_action)
        
        # About action
        about_action = QAction("About", self)
        about_action.setToolTip(f"About {APP_NAME}")
        about_action.triggered.connect(self.about_requested.emit)
        self.context_menu.addAction(about_action)
        
        self.context_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.setToolTip(f"Exit {APP_NAME}")
        quit_action.triggered.connect(self.exit_requested.emit)
        self.context_menu.addAction(quit_action)
        
        # Set context menu
        if self.tray_icon:
            self.tray_icon.setContextMenu(self.context_menu)
        
        logger.debug("System tray context menu created")
    
    def _setup_connections(self):
        """Setup signal connections."""
        if self.tray_icon:
            # Double-click to show quick editor
            self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.quick_jot_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - could show context menu or quick editor
            # On Windows, right-click shows context menu automatically
            pass
    
    def show_notification(self, title: str, message: str, 
                         icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                         timeout: int = 5000):
        """
        Show a system tray notification message.
        
        Args:
            title: Message title
            message: Message text
            icon: Message icon type
            timeout: Timeout in milliseconds
        """
        if self.tray_icon and self.is_available:
            self.tray_icon.showMessage(title, message, icon, timeout)
    
    def show(self):
        """Show the system tray icon."""
        if self.tray_icon and self.is_available:
            self.tray_icon.show()
            logger.debug("System tray icon shown")
    
    def hide(self):
        """Hide the system tray icon."""
        if self.tray_icon:
            self.tray_icon.hide()
            logger.debug("System tray icon hidden")
    
    def is_visible(self) -> bool:
        """Check if the tray icon is visible."""
        return self.tray_icon and self.tray_icon.isVisible()
    
    def show_message(self, title: str, message: str, 
                    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                    timeout: int = 5000):
        """
        Show a system tray notification message.
        
        Args:
            title: Message title
            message: Message text
            icon: Message icon type
            timeout: Timeout in milliseconds
        """
        if self.tray_icon and self.is_available:
            self.tray_icon.showMessage(title, message, icon, timeout)
    
    def update_recent_files(self, recent_files: list):
        """Update the recent files submenu."""
        if not self.context_menu:
            return
        
        # Find recent menu
        recent_menu = None
        for action in self.context_menu.actions():
            if action.menu() and action.text() == "Recent":
                recent_menu = action.menu()
                break
        
        if not recent_menu:
            return
        
        # Clear existing actions
        recent_menu.clear()
        
        if not recent_files:
            no_recent_action = QAction("No recent files", self)
            no_recent_action.setEnabled(False)
            recent_menu.addAction(no_recent_action)
        else:
            for i, file_path in enumerate(recent_files[:10]):  # Limit to 10 files
                file_name = Path(file_path).name
                action = QAction(f"{i+1}. {file_name}", self)
                action.setToolTip(file_path)
                action.setData(file_path)  # Store full path
                # Connect to signal to open file (would need to be implemented)
                recent_menu.addAction(action)


class DockModeManager(QObject):
    """
    Manages the dock mode switching between corner launcher and system tray.
    """
    
    # Signals
    mode_changed = Signal(str)  # Emits new mode: "corner" or "tray"
    
    def __init__(self, launcher_manager=None, tray_manager=None, parent=None):
        super().__init__(parent)
        
        self.launcher_manager = launcher_manager
        self.tray_manager = tray_manager
        self.current_mode = get_setting("dock_mode", "corner")
        
        # Apply current mode
        self._apply_mode(self.current_mode)
        
        logger.info(f"Dock mode manager initialized with mode: {self.current_mode}")
    
    def set_mode(self, mode: str):
        """
        Set the dock mode.
        
        Args:
            mode: "corner" or "tray"
        """
        if mode not in ["corner", "tray"]:
            logger.error(f"Invalid dock mode: {mode}")
            return
        
        if mode == self.current_mode:
            return
        
        old_mode = self.current_mode
        self.current_mode = mode
        
        # Save to settings
        set_setting("dock_mode", mode)
        
        # Apply new mode
        self._apply_mode(mode)
        
        # Emit signal
        self.mode_changed.emit(mode)
        
        logger.info(f"Dock mode changed from {old_mode} to {mode}")
    
    def _apply_mode(self, mode: str):
        """Apply the specified dock mode."""
        if mode == "corner":
            # Show corner launcher, hide tray
            if self.launcher_manager:
                self.launcher_manager.set_launcher_visible(True)
            if self.tray_manager:
                self.tray_manager.hide()
                
        elif mode == "tray":
            # Show tray, hide corner launcher
            if self.tray_manager and self.tray_manager.is_available:
                self.tray_manager.show()
            else:
                # Fallback to corner mode if tray not available
                logger.warning("System tray not available, falling back to corner mode")
                self.current_mode = "corner"
                set_setting("dock_mode", "corner")
                mode = "corner"
            
            if self.launcher_manager:
                self.launcher_manager.set_launcher_visible(False)
    
    def get_current_mode(self) -> str:
        """Get the current dock mode."""
        return self.current_mode
    
    def get_mode(self) -> str:
        """Get the current dock mode (alias for get_current_mode)."""
        return self.current_mode
    
    def is_tray_mode(self) -> bool:
        """Check if currently in tray mode."""
        return self.current_mode == "tray"
    
    def is_corner_mode(self) -> bool:
        """Check if currently in corner mode."""
        return self.current_mode == "corner"
    
    def is_tray_available(self) -> bool:
        """Check if system tray is available."""
        return self.tray_manager and self.tray_manager.is_available
    
    def toggle_mode(self):
        """Toggle between corner and tray modes."""
        new_mode = "tray" if self.current_mode == "corner" else "corner"
        self.set_mode(new_mode)


class StartupManager:
    """
    Manages application startup settings (Windows registry integration).
    """
    
    def __init__(self):
        self.app_name = APP_NAME
        self.is_windows = sys.platform.startswith('win')
        
        # Get executable path for startup command
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.executable_path = sys.executable
        else:
            # Running as Python script
            self.executable_path = sys.executable
        
    def is_startup_enabled(self) -> bool:
        """Check if the application is set to start with Windows."""
        if not self.is_windows:
            return False
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                try:
                    winreg.QueryValueEx(key, self.app_name)
                    return True
                except FileNotFoundError:
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking startup status: {e}")
            return False
    
    def set_startup_enabled(self, enabled: bool) -> bool:
        """
        Enable or disable application startup with Windows.
        
        Args:
            enabled: True to enable startup, False to disable
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_windows:
            logger.warning("Startup management is only supported on Windows")
            return False
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            if enabled:
                # Add to startup
                executable_path = sys.executable
                if getattr(sys, 'frozen', False):
                    # Running as compiled executable
                    executable_path = sys.executable
                else:
                    # Running as Python script, need to include script path
                    script_path = Path(__file__).parent.parent.parent.parent / "launch.bat"
                    if script_path.exists():
                        executable_path = str(script_path)
                    else:
                        # Fallback to python + module
                        executable_path = f'"{sys.executable}" -m pocket_journal'
                
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, executable_path)
                
                logger.info(f"Added {self.app_name} to Windows startup")
                return True
                
            else:
                # Remove from startup
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                                      winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, self.app_name)
                    
                    logger.info(f"Removed {self.app_name} from Windows startup")
                    return True
                    
                except FileNotFoundError:
                    # Already not in startup
                    return True
                    
        except Exception as e:
            logger.error(f"Error setting startup status: {e}")
            return False
    
    def get_startup_command(self) -> Optional[str]:
        """Get the current startup command if enabled."""
        if not self.is_windows:
            return None
            
        if not self.is_startup_enabled():
            return None
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return value
                
        except Exception as e:
            logger.error(f"Error getting startup command: {e}")
            return None