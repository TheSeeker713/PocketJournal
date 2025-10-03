"""
Launcher manager that coordinates the micro-launcher and editor panel.

This module manages the interaction between the circular launcher and
the expandable editor panel, including animations and state management.
It also handles dock mode switching between corner launcher and system tray.
"""

import logging
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QKeySequence

from .micro_launcher import CircularLauncher
from .editor_panel_integrated import IntegratedEditorPanel
from .system_tray import SystemTrayManager, DockModeManager
from ..settings import settings, get_setting

logger = logging.getLogger(__name__)


class LauncherManager(QObject):
    """
    Manages the micro-launcher system including the circular launcher,
    the expandable editor panel, and dock mode switching.
    
    Features:
    - Coordinates between launcher and panel
    - Handles dock mode (corner vs tray)
    - Manages expand/collapse animations
    - Persists state and settings
    - Integrates with system tray
    """
    
    # Signals
    launcher_shown = Signal()
    launcher_hidden = Signal()
    panel_expanded = Signal()
    panel_collapsed = Signal()
    dock_mode_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Components
        self.circular_launcher = None
        self.editor_panel = None
        self.system_tray = None
        self.dock_mode_manager = DockModeManager()
        
        # State
        self.is_panel_expanded = False
        self.launcher_visible = True
        self.current_dock_mode = get_setting("dock_mode", "corner")
        
        # Initialize components based on dock mode
        self.setup_components()
        
        # Setup global hotkey (simplified - in a real app you'd use a proper global hotkey library)
        self.setup_hotkey_simulation()
    
    def setup_components(self):
        """Initialize the launcher components based on dock mode."""
        # Determine dock mode
        dock_mode = get_setting("dock_mode", "corner")
        
        if dock_mode == "tray":
            self.setup_tray_mode()
        else:
            self.setup_corner_mode()
        
        # Create editor panel (always needed regardless of dock mode)
        self.editor_panel = IntegratedEditorPanel()
        self.editor_panel.collapse_requested.connect(self.collapse_panel)
        
        logger.debug(f"Launcher components setup for {dock_mode} mode")
    
    def setup_corner_mode(self):
        """Setup for corner launcher mode."""
        # Create circular launcher
        self.circular_launcher = CircularLauncher()
        self.circular_launcher.expand_requested.connect(self.expand_panel)
        self.circular_launcher.collapse_requested.connect(self.collapse_panel)
        
        # Hide tray if it exists
        if self.system_tray:
            self.system_tray.hide()
            self.system_tray = None
        
        # Show launcher
        self.show_launcher()
    
    def setup_tray_mode(self):
        """Setup for system tray mode."""
        # Hide corner launcher if it exists
        if self.circular_launcher:
            self.circular_launcher.hide()
            self.circular_launcher = None
            self.launcher_visible = False
        
        # Create system tray
        self.system_tray = SystemTrayManager()
        
        # Connect tray signals
        self.system_tray.quick_jot_requested.connect(self.expand_panel)
        self.system_tray.show_window_requested.connect(self.show_main_window)
        self.system_tray.settings_requested.connect(self.show_settings)
        self.system_tray.exit_requested.connect(self.quit_application)
        
        # Show tray
        self.system_tray.show()
    
    def switch_dock_mode(self, new_mode: str):
        """
        Switch between dock modes.
        
        Args:
            new_mode: Either "corner" or "tray"
        """
        if new_mode == self.current_dock_mode:
            return
        
        logger.info(f"Switching dock mode from {self.current_dock_mode} to {new_mode}")
        
        # Collapse panel if expanded
        if self.is_panel_expanded:
            self.collapse_panel()
        
        # Update mode
        self.current_dock_mode = new_mode
        
        # Reinitialize components
        if new_mode == "tray":
            self.setup_tray_mode()
        else:
            self.setup_corner_mode()
        
        self.dock_mode_changed.emit(new_mode)
    
    def setup_hotkey_simulation(self):
        """Setup hotkey simulation (in real app, use proper global hotkey library)."""
        # For demo purposes, we'll use a timer to check for the hotkey
        # In a real application, you'd want to use a proper global hotkey library
        # like pynput or register system-wide hotkeys
        
        self.hotkey_timer = QTimer()
        self.hotkey_timer.timeout.connect(self.check_hotkey_simulation)
        # We won't start this timer for now as it would be intrusive in demo
    
    def check_hotkey_simulation(self):
        """Check for hotkey simulation (placeholder)."""
        # This is a placeholder for actual global hotkey functionality
        # In reality, you'd integrate with system hotkey APIs
        pass
    
    def show_launcher(self):
        """Show the circular launcher (corner mode only)."""
        if self.current_dock_mode == "corner" and self.circular_launcher and not self.launcher_visible:
            self.circular_launcher.show()
            self.launcher_visible = True
            self.launcher_shown.emit()
    
    def hide_launcher(self):
        """Hide the circular launcher (corner mode only)."""
        if self.current_dock_mode == "corner" and self.circular_launcher and self.launcher_visible:
            self.circular_launcher.hide()
            self.launcher_visible = False
            self.launcher_hidden.emit()
    
    def expand_panel(self):
        """Expand the editor panel from the appropriate position."""
        if self.is_panel_expanded:
            # If already expanded, just focus it
            if self.editor_panel:
                self.editor_panel.raise_()
                self.editor_panel.activateWindow()
            return
        
        if not self.editor_panel:
            return
        
        if self.current_dock_mode == "corner":
            # Expand from launcher position
            if not self.circular_launcher:
                return
                
            # Get launcher position and size
            launcher_pos = self.circular_launcher.pos()
            launcher_size = self.circular_launcher.size()
            
            # Update panel's corner position based on launcher's current corner
            self.editor_panel.corner_position = self.circular_launcher.last_corner
            
            # Hide launcher and expand panel
            self.hide_launcher()
            self.editor_panel.expand_from_position(launcher_pos, launcher_size)
        else:
            # Tray mode - expand from screen center or corner
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # Use default corner position for tray mode
            self.editor_panel.corner_position = "bottom_right"
            
            # Calculate position for bottom-right corner
            panel_width = self.editor_panel.target_width
            panel_height = self.editor_panel.target_height
            
            x = screen_geometry.right() - panel_width - 20
            y = screen_geometry.bottom() - panel_height - 20
            
            # Expand from calculated position
            self.editor_panel.expand_from_position((x, y), (48, 48))
        
        self.is_panel_expanded = True
        self.panel_expanded.emit()
    
    def collapse_panel(self):
        """Collapse the editor panel back to appropriate position."""
        if not self.is_panel_expanded:
            return
        
        if not self.editor_panel:
            return
        
        if self.current_dock_mode == "corner":
            # Collapse to launcher position
            if not self.circular_launcher:
                return
                
            # Calculate launcher position based on current corner
            self.circular_launcher.last_corner = self.editor_panel.corner_position
            self.circular_launcher.position_at_corner()
            
            # Get target position and size
            target_pos = self.circular_launcher.pos()
            target_size = self.circular_launcher.size()
            
            # Collapse panel to launcher position
            self.editor_panel.collapse_to_position(target_pos, target_size)
            
            # Show launcher after a short delay to allow animation to complete
            QTimer.singleShot(300, self.show_launcher)
        else:
            # Tray mode - just hide the panel
            self.editor_panel.hide()
        
        self.is_panel_expanded = False
        self.panel_collapsed.emit()
    
    def toggle_panel(self):
        """Toggle between expanded and collapsed states."""
        if self.is_panel_expanded:
            self.collapse_panel()
        else:
            self.expand_panel()
    
    def set_launcher_visible(self, visible: bool):
        """Set launcher visibility (corner mode only)."""
        if self.current_dock_mode == "corner":
            if visible:
                self.show_launcher()
            else:
                self.hide_launcher()
    
    def get_launcher_position(self):
        """Get the current launcher position."""
        if self.circular_launcher:
            return self.circular_launcher.pos()
        return None
    
    def get_launcher_corner(self):
        """Get the current launcher corner."""
        if self.circular_launcher:
            return self.circular_launcher.last_corner
        return "bottom_right"
    
    def set_launcher_corner(self, corner: str):
        """Set the launcher corner and reposition it."""
        if self.circular_launcher:
            self.circular_launcher.last_corner = corner
            self.circular_launcher.position_at_corner()
            self.circular_launcher.save_settings()
    
    def show_main_window(self):
        """Show the main application window (for tray mode)."""
        # This will be connected to the main window's show method
        pass
    
    def show_settings(self):
        """Show settings dialog (for tray mode)."""
        # This will be connected to show the settings dialog
        pass
    
    def quit_application(self):
        """Quit the application (for tray mode)."""
        # This will be connected to QApplication.quit
        pass
    
    def shutdown(self):
        """Cleanup when shutting down."""
        # Save any pending content
        if self.editor_panel:
            self.editor_panel.save_content()
        
        # Save settings
        if self.circular_launcher:
            self.circular_launcher.save_settings()
        
        if self.editor_panel:
            self.editor_panel.save_settings()
        
        # Hide components
        if self.circular_launcher:
            self.circular_launcher.hide()
        
        if self.editor_panel:
            self.editor_panel.hide()
        
        if self.system_tray:
            self.system_tray.hide()


class GlobalHotkeyHandler(QObject):
    """
    Placeholder for global hotkey handling.
    
    In a production app, this would integrate with system APIs or
    third-party libraries like pynput for global hotkey detection.
    """
    
    hotkey_activated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hotkey_combination = settings.get("hotkey", "Ctrl+Alt+J")
        self.enabled = True
    
    def set_hotkey(self, hotkey_combination: str):
        """Set the global hotkey combination."""
        self.hotkey_combination = hotkey_combination
        settings.set("hotkey", hotkey_combination)
        # In real implementation, would unregister old and register new hotkey
    
    def enable(self):
        """Enable global hotkey detection."""
        self.enabled = True
        # In real implementation, would register system hotkey
    
    def disable(self):
        """Disable global hotkey detection."""
        self.enabled = False
        # In real implementation, would unregister system hotkey