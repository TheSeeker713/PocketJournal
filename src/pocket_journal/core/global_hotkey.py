"""
Global hotkey registration system for PocketJournal.

This module handles system-wide hotkey registration to expand the editor panel
when the application is running in the background.
"""

import logging
import sys
import platform
from typing import Optional, Callable, Dict
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


@dataclass
class HotkeyBinding:
    """Represents a hotkey binding."""
    key_combination: str
    callback: Callable
    description: str
    enabled: bool = True


class GlobalHotkeyManager(QObject):
    """
    Manages global hotkey registration across platforms.
    
    Uses platform-specific implementations for actual hotkey registration.
    Provides a unified interface for the application.
    """
    
    # Signals
    hotkey_activated = Signal(str)  # hotkey combination
    registration_failed = Signal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.hotkeys: Dict[str, HotkeyBinding] = {}
        self.platform_manager = None
        self._init_platform_manager()
        
        logger.debug("Global hotkey manager initialized")
    
    def _init_platform_manager(self):
        """Initialize platform-specific hotkey manager."""
        system = platform.system().lower()
        
        if system == 'windows':
            try:
                self.platform_manager = WindowsHotkeyManager(self)
            except ImportError as e:
                logger.warning(f"Windows hotkey support not available: {e}")
                self.platform_manager = FallbackHotkeyManager(self)
        elif system == 'darwin':  # macOS
            try:
                self.platform_manager = MacOSHotkeyManager(self)
            except ImportError as e:
                logger.warning(f"macOS hotkey support not available: {e}")
                self.platform_manager = FallbackHotkeyManager(self)
        elif system == 'linux':
            try:
                self.platform_manager = LinuxHotkeyManager(self)
            except ImportError as e:
                logger.warning(f"Linux hotkey support not available: {e}")
                self.platform_manager = FallbackHotkeyManager(self)
        else:
            logger.warning(f"Unsupported platform: {system}")
            self.platform_manager = FallbackHotkeyManager(self)
    
    def register_hotkey(self, key_combination: str, callback: Callable, description: str = "") -> bool:
        """
        Register a global hotkey.
        
        Args:
            key_combination: Hotkey string like "Ctrl+Alt+J"
            callback: Function to call when hotkey is pressed
            description: Human-readable description
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Create hotkey binding
            binding = HotkeyBinding(
                key_combination=key_combination,
                callback=callback,
                description=description
            )
            
            # Register with platform manager
            success = self.platform_manager.register(key_combination, callback)
            
            if success:
                self.hotkeys[key_combination] = binding
                logger.info(f"Registered global hotkey: {key_combination}")
                return True
            else:
                logger.error(f"Failed to register hotkey: {key_combination}")
                self.registration_failed.emit(f"Failed to register {key_combination}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering hotkey {key_combination}: {e}")
            self.registration_failed.emit(f"Error: {str(e)}")
            return False
    
    def unregister_hotkey(self, key_combination: str) -> bool:
        """
        Unregister a global hotkey.
        
        Args:
            key_combination: Hotkey string to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if key_combination in self.hotkeys:
                success = self.platform_manager.unregister(key_combination)
                
                if success:
                    del self.hotkeys[key_combination]
                    logger.info(f"Unregistered global hotkey: {key_combination}")
                    return True
                else:
                    logger.error(f"Failed to unregister hotkey: {key_combination}")
                    return False
            else:
                logger.warning(f"Hotkey not registered: {key_combination}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering hotkey {key_combination}: {e}")
            return False
    
    def update_hotkey(self, old_combination: str, new_combination: str, callback: Callable, description: str = "") -> bool:
        """
        Update an existing hotkey registration.
        
        Args:
            old_combination: Current hotkey string
            new_combination: New hotkey string
            callback: Function to call when hotkey is pressed
            description: Human-readable description
            
        Returns:
            True if update successful, False otherwise
        """
        # Unregister old hotkey
        if old_combination in self.hotkeys:
            self.unregister_hotkey(old_combination)
        
        # Register new hotkey
        return self.register_hotkey(new_combination, callback, description)
    
    def is_registered(self, key_combination: str) -> bool:
        """Check if a hotkey is currently registered."""
        return key_combination in self.hotkeys
    
    def get_registered_hotkeys(self) -> Dict[str, HotkeyBinding]:
        """Get all currently registered hotkeys."""
        return self.hotkeys.copy()
    
    def is_available(self) -> bool:
        """Check if global hotkey support is available on this platform."""
        return self.platform_manager is not None and self.platform_manager.is_available()
    
    def cleanup(self):
        """Cleanup and unregister all hotkeys."""
        try:
            for key_combination in list(self.hotkeys.keys()):
                self.unregister_hotkey(key_combination)
                
            if self.platform_manager:
                self.platform_manager.cleanup()
                
            logger.debug("Global hotkey manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during hotkey cleanup: {e}")


class WindowsHotkeyManager(QObject):
    """Windows-specific hotkey manager using win32api."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Try to import Windows-specific modules
        try:
            import win32con
            import win32gui
            import win32api
            self.win32con = win32con
            self.win32gui = win32gui
            self.win32api = win32api
            self.available = True
        except ImportError:
            logger.warning("Windows hotkey modules not available (win32api required)")
            self.available = False
            
        self.registered_hotkeys = {}
        self.hotkey_id_counter = 1
        
    def is_available(self) -> bool:
        """Check if Windows hotkey support is available."""
        return self.available
        
    def register(self, key_combination: str, callback: Callable) -> bool:
        """Register a Windows global hotkey."""
        if not self.available:
            return False
            
        try:
            # Parse key combination (simplified for demo)
            # In production, you'd want a more robust parser
            modifiers = 0
            key_code = None
            
            parts = key_combination.split('+')
            for part in parts:
                part = part.strip().lower()
                if part == 'ctrl':
                    modifiers |= self.win32con.MOD_CONTROL
                elif part == 'alt':
                    modifiers |= self.win32con.MOD_ALT
                elif part == 'shift':
                    modifiers |= self.win32con.MOD_SHIFT
                elif part == 'win':
                    modifiers |= self.win32con.MOD_WIN
                elif len(part) == 1:
                    key_code = ord(part.upper())
                else:
                    # Handle special keys
                    special_keys = {
                        'space': self.win32con.VK_SPACE,
                        'enter': self.win32con.VK_RETURN,
                        'escape': self.win32con.VK_ESCAPE,
                        'tab': self.win32con.VK_TAB,
                        'f1': self.win32con.VK_F1,
                        'f2': self.win32con.VK_F2,
                        'f3': self.win32con.VK_F3,
                        'f4': self.win32con.VK_F4,
                        'f5': self.win32con.VK_F5,
                        'f6': self.win32con.VK_F6,
                        'f7': self.win32con.VK_F7,
                        'f8': self.win32con.VK_F8,
                        'f9': self.win32con.VK_F9,
                        'f10': self.win32con.VK_F10,
                        'f11': self.win32con.VK_F11,
                        'f12': self.win32con.VK_F12,
                    }
                    key_code = special_keys.get(part)
            
            if key_code is None:
                logger.error(f"Invalid key combination: {key_combination}")
                return False
            
            # Get application window handle
            app = QApplication.instance()
            if app and hasattr(app, 'activeWindow') and app.activeWindow():
                hwnd = int(app.activeWindow().winId())
            else:
                # Fallback to any Qt window
                hwnd = None
                for widget in QApplication.topLevelWidgets():
                    if widget.isVisible():
                        hwnd = int(widget.winId())
                        break
                        
                if hwnd is None:
                    logger.error("No valid window handle found for hotkey registration")
                    return False
            
            # Register hotkey
            hotkey_id = self.hotkey_id_counter
            self.hotkey_id_counter += 1
            
            success = self.win32gui.RegisterHotKey(hwnd, hotkey_id, modifiers, key_code)
            
            if success:
                self.registered_hotkeys[key_combination] = {
                    'id': hotkey_id,
                    'hwnd': hwnd,
                    'callback': callback
                }
                
                # Start polling for hotkey messages (simplified approach)
                self._start_message_polling()
                
                return True
            else:
                logger.error(f"RegisterHotKey failed for {key_combination}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering Windows hotkey: {e}")
            return False
    
    def unregister(self, key_combination: str) -> bool:
        """Unregister a Windows global hotkey."""
        if not self.available or key_combination not in self.registered_hotkeys:
            return False
            
        try:
            hotkey_info = self.registered_hotkeys[key_combination]
            success = self.win32gui.UnregisterHotKey(hotkey_info['hwnd'], hotkey_info['id'])
            
            if success:
                del self.registered_hotkeys[key_combination]
                return True
            else:
                logger.error(f"UnregisterHotKey failed for {key_combination}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering Windows hotkey: {e}")
            return False
    
    def _start_message_polling(self):
        """Start polling for Windows hotkey messages."""
        # In a real implementation, you'd use a proper Windows message loop
        # For this demo, we'll use a simplified timer-based approach
        if not hasattr(self, 'poll_timer'):
            self.poll_timer = QTimer()
            self.poll_timer.timeout.connect(self._poll_messages)
            self.poll_timer.start(50)  # Poll every 50ms
    
    def _poll_messages(self):
        """Poll for Windows hotkey messages (simplified)."""
        # This is a simplified approach for demo purposes
        # In production, you'd integrate with the Windows message loop properly
        pass
    
    def cleanup(self):
        """Cleanup Windows hotkey registrations."""
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
            
        for key_combination in list(self.registered_hotkeys.keys()):
            self.unregister(key_combination)


class MacOSHotkeyManager(QObject):
    """macOS-specific hotkey manager using Cocoa."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Try to import macOS-specific modules
        try:
            # In a real implementation, you'd use PyObjC or similar
            # For demo purposes, we'll simulate availability
            self.available = sys.platform == 'darwin'
        except ImportError:
            logger.warning("macOS hotkey modules not available")
            self.available = False
            
        self.registered_hotkeys = {}
    
    def is_available(self) -> bool:
        """Check if macOS hotkey support is available."""
        return self.available
        
    def register(self, key_combination: str, callback: Callable) -> bool:
        """Register a macOS global hotkey."""
        if not self.available:
            return False
            
        # Simplified implementation for demo
        logger.info(f"Simulating macOS hotkey registration: {key_combination}")
        self.registered_hotkeys[key_combination] = callback
        return True
    
    def unregister(self, key_combination: str) -> bool:
        """Unregister a macOS global hotkey."""
        if key_combination in self.registered_hotkeys:
            del self.registered_hotkeys[key_combination]
            logger.info(f"Simulating macOS hotkey unregistration: {key_combination}")
            return True
        return False
    
    def cleanup(self):
        """Cleanup macOS hotkey registrations."""
        self.registered_hotkeys.clear()


class LinuxHotkeyManager(QObject):
    """Linux-specific hotkey manager using X11."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Try to import Linux-specific modules
        try:
            # In a real implementation, you'd use python-xlib or similar
            # For demo purposes, we'll simulate availability
            self.available = sys.platform.startswith('linux')
        except ImportError:
            logger.warning("Linux hotkey modules not available")
            self.available = False
            
        self.registered_hotkeys = {}
    
    def is_available(self) -> bool:
        """Check if Linux hotkey support is available."""
        return self.available
        
    def register(self, key_combination: str, callback: Callable) -> bool:
        """Register a Linux global hotkey."""
        if not self.available:
            return False
            
        # Simplified implementation for demo
        logger.info(f"Simulating Linux hotkey registration: {key_combination}")
        self.registered_hotkeys[key_combination] = callback
        return True
    
    def unregister(self, key_combination: str) -> bool:
        """Unregister a Linux global hotkey."""
        if key_combination in self.registered_hotkeys:
            del self.registered_hotkeys[key_combination]
            logger.info(f"Simulating Linux hotkey unregistration: {key_combination}")
            return True
        return False
    
    def cleanup(self):
        """Cleanup Linux hotkey registrations."""
        self.registered_hotkeys.clear()


class FallbackHotkeyManager(QObject):
    """Fallback hotkey manager when platform-specific support is unavailable."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registered_hotkeys = {}
    
    def is_available(self) -> bool:
        """Fallback manager is not fully functional."""
        return False
        
    def register(self, key_combination: str, callback: Callable) -> bool:
        """Simulate hotkey registration."""
        logger.warning(f"Global hotkey not supported on this platform, simulating: {key_combination}")
        self.registered_hotkeys[key_combination] = callback
        return True
    
    def unregister(self, key_combination: str) -> bool:
        """Simulate hotkey unregistration."""
        if key_combination in self.registered_hotkeys:
            del self.registered_hotkeys[key_combination]
            return True
        return False
    
    def cleanup(self):
        """Cleanup fallback registrations."""
        self.registered_hotkeys.clear()


# Convenience function for creating a global hotkey manager
def create_global_hotkey_manager() -> GlobalHotkeyManager:
    """Create and return a global hotkey manager instance."""
    return GlobalHotkeyManager()