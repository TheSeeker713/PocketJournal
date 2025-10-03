"""
Micro-launcher widget - the small circular "book circle" that stays on top.

This module implements the always-on-top circular launcher that can expand
into the main editor panel with smooth animations.
"""

import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize,
    Signal, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPainterPath,
    QMouseEvent, QKeyEvent, QIcon
)

from ..settings import settings


class CircularLauncher(QWidget):
    """
    Circular launcher widget that stays always on top.
    
    Features:
    - Frameless, circular appearance
    - Always on top
    - Draggable
    - Snap to nearest corner
    - Click to expand/collapse
    """
    
    # Signals
    expand_requested = Signal()
    collapse_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration
        self.circle_size = 48  # Default size
        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.snap_threshold = 100  # Distance from corner to snap
        
        # Load settings
        self.load_settings()
        
        # Setup window properties
        self.setup_window()
        
        # Setup UI
        self.setup_ui()
        
        # Position at last known corner
        self.position_at_corner()
    
    def setup_window(self):
        """Configure window properties for the circular launcher."""
        # Make window frameless and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Set fixed size
        self.setFixedSize(self.circle_size, self.circle_size)
        
        # Make window ignore mouse events for transparency effect
        # but still receive clicks on the visible circle
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
    
    def setup_ui(self):
        """Setup the UI elements for the circular launcher."""
        # Create layout (though we'll paint custom)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    def load_settings(self):
        """Load launcher settings from configuration."""
        self.last_corner = settings.get("launcher.last_corner", "top-right")
        self.circle_size = settings.get("launcher.circle_size", 48)
        
        # Validate circle size
        self.circle_size = max(32, min(64, self.circle_size))
    
    def save_settings(self):
        """Save current launcher settings."""
        settings.set("launcher.last_corner", self.last_corner)
        settings.set("launcher.circle_size", self.circle_size)
    
    def position_at_corner(self):
        """Position the launcher at the saved corner."""
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20  # Distance from screen edge
        
        if self.last_corner == "top-left":
            x, y = margin, margin
        elif self.last_corner == "top-right":
            x, y = screen.width() - self.circle_size - margin, margin
        elif self.last_corner == "bottom-left":
            x, y = margin, screen.height() - self.circle_size - margin
        else:  # bottom-right (default)
            x, y = screen.width() - self.circle_size - margin, screen.height() - self.circle_size - margin
        
        self.move(x, y)
    
    def get_nearest_corner(self, pos: QPoint) -> str:
        """Determine which corner is nearest to the given position."""
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Calculate distances to each corner
        corners = {
            "top-left": QPoint(0, 0),
            "top-right": QPoint(screen.width() - self.circle_size, 0),
            "bottom-left": QPoint(0, screen.height() - self.circle_size),
            "bottom-right": QPoint(screen.width() - self.circle_size, screen.height() - self.circle_size)
        }
        
        min_distance = float('inf')
        nearest_corner = "top-right"
        
        for corner_name, corner_pos in corners.items():
            distance = math.sqrt(
                (pos.x() - corner_pos.x()) ** 2 + 
                (pos.y() - corner_pos.y()) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                nearest_corner = corner_name
        
        return nearest_corner
    
    def snap_to_nearest_corner(self):
        """Snap the launcher to the nearest corner with animation."""
        current_pos = self.pos()
        nearest_corner = self.get_nearest_corner(current_pos)
        
        # Update last corner setting
        self.last_corner = nearest_corner
        self.save_settings()
        
        # Animate to corner position
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        
        if nearest_corner == "top-left":
            target_pos = QPoint(margin, margin)
        elif nearest_corner == "top-right":
            target_pos = QPoint(screen.width() - self.circle_size - margin, margin)
        elif nearest_corner == "bottom-left":
            target_pos = QPoint(margin, screen.height() - self.circle_size - margin)
        else:  # bottom-right
            target_pos = QPoint(screen.width() - self.circle_size - margin, screen.height() - self.circle_size - margin)
        
        # Create snap animation
        self.snap_animation = QPropertyAnimation(self, b"pos")
        self.snap_animation.setDuration(200)
        self.snap_animation.setStartValue(current_pos)
        self.snap_animation.setEndValue(target_pos)
        self.snap_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.snap_animation.start()
    
    def paintEvent(self, event):
        """Custom paint event to draw the circular launcher."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        
        # Draw circle background
        circle_rect = self.rect().adjusted(4, 4, -4, -4)  # Account for shadow
        
        # Gradient background
        center = circle_rect.center()
        gradient_brush = QBrush(QColor(45, 140, 240))  # Nice blue color
        
        # Draw main circle
        painter.setBrush(gradient_brush)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.drawEllipse(circle_rect)
        
        # Draw book icon (simplified)
        icon_rect = circle_rect.adjusted(12, 12, -12, -12)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Simple book shape
        book_rect = icon_rect.adjusted(2, 4, -2, -4)
        painter.drawRect(book_rect)
        
        # Book pages
        page_x = book_rect.left() + 4
        painter.drawLine(page_x, book_rect.top(), page_x, book_rect.bottom())
        page_x = book_rect.left() + 7
        painter.drawLine(page_x, book_rect.top(), page_x, book_rect.bottom())
        
        painter.end()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for dragging and clicking."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint() - self.pos()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events for dragging."""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                # End dragging and snap to nearest corner
                self.is_dragging = False
                
                # Small delay before snapping to feel natural
                QTimer.singleShot(100, self.snap_to_nearest_corner)
            else:
                # If not dragging, treat as click to expand
                self.expand_requested.emit()
            
            event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double-click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Double-click to expand
            self.expand_requested.emit()
            event.accept()
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        # Slight scale animation on hover
        self.setStyleSheet("QWidget { border: 2px solid rgba(255, 255, 255, 100); border-radius: 24px; }")
        
        # Show recent entries popover after a short delay
        if not hasattr(self, 'hover_timer'):
            self.hover_timer = QTimer()
            self.hover_timer.setSingleShot(True)
            self.hover_timer.timeout.connect(self._show_recent_popover)
        
        self.hover_timer.start(800)  # 800ms delay before showing popover
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self.setStyleSheet("")
        
        # Cancel hover timer
        if hasattr(self, 'hover_timer'):
            self.hover_timer.stop()
            
        # Hide popover after a short delay (gives time to move mouse to popover)
        if hasattr(self, 'recent_popover') and self.recent_popover.isVisible():
            if not hasattr(self, 'hide_timer'):
                self.hide_timer = QTimer()
                self.hide_timer.setSingleShot(True)
                self.hide_timer.timeout.connect(self._hide_recent_popover)
            self.hide_timer.start(200)  # 200ms delay before hiding
            
        super().leaveEvent(event)
        
    def _show_recent_popover(self):
        """Show the recent entries popover."""
        if not hasattr(self, 'recent_popover'):
            from .recent_and_search import RecentEntriesPopover
            self.recent_popover = RecentEntriesPopover()
            self.recent_popover.entry_selected.connect(self._on_recent_entry_selected)
            
        # Cancel any pending hide
        if hasattr(self, 'hide_timer'):
            self.hide_timer.stop()
            
        # Show popover positioned near launcher
        launcher_pos = self.pos()
        launcher_size = self.size()
        self.recent_popover.show_near_launcher(launcher_pos, launcher_size)
        
    def _hide_recent_popover(self):
        """Hide the recent entries popover."""
        if hasattr(self, 'recent_popover') and self.recent_popover.isVisible():
            self.recent_popover.hide()
            
    def _on_recent_entry_selected(self, file_path: str):
        """Handle recent entry selection."""
        # Hide the popover
        self._hide_recent_popover()
        
        # Emit signal to open the entry
        # For now, just expand the panel - the launcher manager will handle loading the entry
        self.expand_requested.emit()