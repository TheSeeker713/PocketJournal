"""
Launcher manager that coordinates the micro-launcher and editor panel.

This module manages the interaction between the circular launcher and
the expandable editor panel, including animations and state management.
"""

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QKeySequence

from .micro_launcher import CircularLauncher
from .editor_panel import QuickEditorPanel
from ..settings import settings


class LauncherManager(QObject):
    """
    Manages the micro-launcher system including the circular launcher
    and the expandable editor panel.
    
    Features:
    - Coordinates between launcher and panel
    - Handles global hotkey
    - Manages expand/collapse animations
    - Persists state and settings
    """
    
    # Signals
    launcher_shown = Signal()
    launcher_hidden = Signal()
    panel_expanded = Signal()
    panel_collapsed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Components
        self.circular_launcher = None
        self.editor_panel = None
        
        # State
        self.is_panel_expanded = False
        self.launcher_visible = True
        
        # Initialize components
        self.setup_components()
        
        # Setup global hotkey (simplified - in a real app you'd use a proper global hotkey library)
        self.setup_hotkey_simulation()
    
    def setup_components(self):
        """Initialize the launcher components."""
        # Create circular launcher
        self.circular_launcher = CircularLauncher()
        self.circular_launcher.expand_requested.connect(self.expand_panel)
        self.circular_launcher.collapse_requested.connect(self.collapse_panel)
        
        # Create editor panel
        self.editor_panel = QuickEditorPanel()
        self.editor_panel.collapse_requested.connect(self.collapse_panel)
        
        # Initially show only the launcher
        self.show_launcher()
    
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
        """Show the circular launcher."""
        if self.circular_launcher and not self.launcher_visible:
            self.circular_launcher.show()
            self.launcher_visible = True
            self.launcher_shown.emit()
    
    def hide_launcher(self):
        """Hide the circular launcher."""
        if self.circular_launcher and self.launcher_visible:
            self.circular_launcher.hide()
            self.launcher_visible = False
            self.launcher_hidden.emit()
    
    def expand_panel(self):
        """Expand the editor panel from the launcher position."""
        if self.is_panel_expanded:
            # If already expanded, just focus it
            if self.editor_panel:
                self.editor_panel.raise_()
                self.editor_panel.activateWindow()
            return
        
        if not self.circular_launcher or not self.editor_panel:
            return
        
        # Get launcher position and size
        launcher_pos = self.circular_launcher.pos()
        launcher_size = self.circular_launcher.size()
        
        # Update panel's corner position based on launcher's current corner
        self.editor_panel.corner_position = self.circular_launcher.last_corner
        
        # Hide launcher and expand panel
        self.hide_launcher()
        self.editor_panel.expand_from_position(launcher_pos, launcher_size)
        
        self.is_panel_expanded = True
        self.panel_expanded.emit()
    
    def collapse_panel(self):
        """Collapse the editor panel back to launcher."""
        if not self.is_panel_expanded:
            return
        
        if not self.circular_launcher or not self.editor_panel:
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
        
        self.is_panel_expanded = False
        self.panel_collapsed.emit()
    
    def toggle_panel(self):
        """Toggle between expanded and collapsed states."""
        if self.is_panel_expanded:
            self.collapse_panel()
        else:
            self.expand_panel()
    
    def set_launcher_visible(self, visible: bool):
        """Set launcher visibility."""
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
        return "top-right"
    
    def set_launcher_corner(self, corner: str):
        """Set the launcher corner and reposition it."""
        if self.circular_launcher:
            self.circular_launcher.last_corner = corner
            self.circular_launcher.position_at_corner()
            self.circular_launcher.save_settings()
    
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