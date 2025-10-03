"""
Enhanced editor panel with minimalist top bar and text area.

This module provides the primary note-taking interface with a clean design
featuring a top icon bar, main text editor, and status strip.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QToolButton,
    QFrame, QSizePolicy, QApplication, QStatusBar, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import (
    QFont, QTextCursor, QKeySequence, QShortcut, QIcon, QPixmap, 
    QPainter, QBrush, QColor, QPen, QAction
)

from ..settings import settings, get_setting, set_setting
from ..app_meta import APP_NAME

logger = logging.getLogger(__name__)


class IconButton(QToolButton):
    """Custom icon button for the top bar."""
    
    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        
        self.icon_name = icon_name
        self.setToolTip(tooltip)
        
        # Set fixed size for consistent appearance
        self.setFixedSize(32, 32)
        
        # Create icon
        self.setIcon(self._create_icon())
        
        # Style the button
        self.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 6px;
                padding: 4px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
    
    def _create_icon(self) -> QIcon:
        """Create a simple icon based on the icon name."""
        size = 20
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set color
        color = QColor(100, 100, 100)
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        
        # Draw different icons based on name
        center = size // 2
        
        if self.icon_name == "back":
            # Left arrow
            painter.drawLine(center + 2, center - 4, center - 2, center)
            painter.drawLine(center - 2, center, center + 2, center + 4)
            painter.drawLine(center - 2, center, center + 6, center)
            
        elif self.icon_name == "search":
            # Magnifying glass
            painter.drawEllipse(center - 4, center - 4, 6, 6)
            painter.drawLine(center + 1, center + 1, center + 4, center + 4)
            
        elif self.icon_name == "export":
            # Upload arrow
            painter.drawLine(center, center - 4, center, center + 4)
            painter.drawLine(center, center - 4, center - 3, center - 1)
            painter.drawLine(center, center - 4, center + 3, center - 1)
            painter.drawRect(center - 4, center + 2, 8, 2)
            
        elif self.icon_name == "tags":
            # Tag icon
            painter.drawRect(center - 4, center - 2, 6, 4)
            painter.drawLine(center + 2, center - 2, center + 4, center)
            painter.drawLine(center + 4, center, center + 2, center + 2)
            painter.drawEllipse(center - 2, center - 1, 2, 2)
            
        elif self.icon_name == "more":
            # Three dots
            painter.drawEllipse(center - 5, center - 1, 2, 2)
            painter.drawEllipse(center - 1, center - 1, 2, 2)
            painter.drawEllipse(center + 3, center - 1, 2, 2)
            
        elif self.icon_name == "settings":
            # Gear icon
            painter.drawEllipse(center - 3, center - 3, 6, 6)
            painter.drawEllipse(center - 1, center - 1, 2, 2)
            for i in range(8):
                angle = i * 45
                painter.save()
                painter.translate(center, center)
                painter.rotate(angle)
                painter.drawRect(-1, -6, 2, 2)
                painter.restore()
                
        elif self.icon_name == "help":
            # Question mark
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")
            
        elif self.icon_name == "egg":
            # Easter egg icon (only shown if enabled)
            painter.drawEllipse(center - 3, center - 4, 6, 8)
            painter.setPen(QPen(QColor(255, 200, 0), 1))
            painter.drawEllipse(center - 1, center - 2, 2, 2)
            
        else:
            # Default icon (square)
            painter.drawRect(center - 3, center - 3, 6, 6)
        
        painter.end()
        return QIcon(pixmap)


class EditorTopBar(QWidget):
    """Top bar with minimalist icons for editor actions."""
    
    # Signals
    back_clicked = Signal()
    search_clicked = Signal()
    export_clicked = Signal()
    tags_clicked = Signal()
    more_clicked = Signal()
    settings_clicked = Signal()
    help_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the top bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Left side icons
        self.back_btn = IconButton("back", "Back/Recent entries")
        self.search_btn = IconButton("search", "Search entries (Ctrl+K)")
        self.export_btn = IconButton("export", "Export entry")
        self.tags_btn = IconButton("tags", "Manage tags")
        self.more_btn = IconButton("more", "More entry actions")
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.tags_btn)
        layout.addWidget(self.more_btn)
        
        # Spacer to push right icons to the right
        layout.addStretch()
        
        # Right side icons
        self.settings_btn = IconButton("settings", "Settings")
        self.help_btn = IconButton("help", "Help (F1)")
        
        # Easter egg icon (only shown if enabled)
        self.egg_btn = IconButton("egg", "Easter egg")
        self.egg_btn.setVisible(get_setting("show_egg_icon", False))
        
        layout.addWidget(self.egg_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.help_btn)
        
        # Style the top bar
        self.setStyleSheet("""
            EditorTopBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
        """)
        
        self.setFixedHeight(40)
    
    def setup_connections(self):
        """Setup signal connections."""
        self.back_btn.clicked.connect(self.back_clicked.emit)
        self.search_btn.clicked.connect(self.search_clicked.emit)
        self.export_btn.clicked.connect(self.export_clicked.emit)
        self.tags_btn.clicked.connect(self.tags_clicked.emit)
        self.more_btn.clicked.connect(self.more_clicked.emit)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.help_btn.clicked.connect(self.help_clicked.emit)
    
    def update_egg_icon_visibility(self):
        """Update easter egg icon visibility based on settings."""
        show_egg = get_setting("show_egg_icon", False) or get_setting("eggs_enabled", True)
        self.egg_btn.setVisible(show_egg)


class EditorStatusBar(QWidget):
    """Bottom status bar with autosave indicator and time."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        
        # Autosave status
        self.autosave_label = QLabel("●")
        self.autosave_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.autosave_label.setToolTip("Autosave active")
        
        # Spacer to push time to the right
        layout.addStretch()
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        layout.addWidget(self.autosave_label)
        layout.addWidget(self.time_label)
        
        # Style the status bar
        self.setStyleSheet("""
            EditorStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e9ecef;
            }
        """)
        
        self.setFixedHeight(24)
        
        # Update time immediately
        self.update_time()
    
    def setup_timer(self):
        """Setup timer for updating the time display."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(30000)  # Update every 30 seconds
    
    def update_time(self):
        """Update the time display in US format."""
        now = datetime.now()
        time_str = now.strftime("%m/%d/%Y %I:%M %p")
        self.time_label.setText(time_str)
    
    def set_autosave_status(self, saving: bool):
        """Update autosave status indicator."""
        if saving:
            self.autosave_label.setText("⚬")
            self.autosave_label.setStyleSheet("""
                QLabel {
                    color: #ffc107;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            self.autosave_label.setToolTip("Saving...")
        else:
            self.autosave_label.setText("●")
            self.autosave_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            self.autosave_label.setToolTip("Autosave active")


class EditorTextArea(QTextEdit):
    """Main text editor with enhanced functionality."""
    
    # Signals
    content_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
    
    def setup_ui(self):
        """Setup the text editor UI."""
        # Set placeholder text
        self.setPlaceholderText("Start typing…")
        
        # Configure font
        font_family = get_setting("font_family", "Segoe UI")
        font_size = get_setting("font_size", 11)
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Enable word wrap
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Set margins and padding
        self.setStyleSheet("""
            EditorTextArea {
                border: none;
                background-color: #ffffff;
                padding: 12px;
                selection-background-color: #007acc;
                selection-color: white;
            }
        """)
        
        # Configure cursor
        self.setCursorWidth(2)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+K for search
        search_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        search_shortcut.activated.connect(self._on_search_shortcut)
        
        # F1 for help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self._on_help_shortcut)
    
    def _on_text_changed(self):
        """Handle text changes."""
        content = self.toPlainText()
        self.content_changed.emit(content)
    
    def _on_search_shortcut(self):
        """Handle Ctrl+K search shortcut."""
        # For now, just log the action
        logger.info("Search shortcut activated (Ctrl+K)")
    
    def _on_help_shortcut(self):
        """Handle F1 help shortcut."""
        # For now, just log the action
        logger.info("Help shortcut activated (F1)")
    
    def focus_editor(self):
        """Focus the editor and position cursor at end."""
        self.setFocus()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)


class EnhancedEditorPanel(QWidget):
    """
    Enhanced editor panel with minimalist top bar and clean text area.
    
    This is the primary note-taking interface featuring:
    - Top icon bar with navigation and action buttons
    - Main text editor with placeholder and responsive design
    - Bottom status bar with autosave indicator and time
    """
    
    # Signals
    close_requested = Signal()
    content_changed = Signal(str)
    new_entry_requested = Signal()
    save_requested = Signal()
    search_requested = Signal()
    settings_requested = Signal()
    help_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_connections()
        
        # Auto-save timer
        self.autosave_timer = QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self._autosave)
        
        # State
        self.is_saving = False
        
        logger.debug("Enhanced editor panel initialized")
    
    def setup_ui(self):
        """Setup the main UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top bar
        self.top_bar = EditorTopBar()
        layout.addWidget(self.top_bar)
        
        # Main text editor
        self.text_editor = EditorTextArea()
        layout.addWidget(self.text_editor)
        
        # Status bar
        self.status_bar = EditorStatusBar()
        layout.addWidget(self.status_bar)
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} - Editor")
        self.setMinimumSize(400, 300)
        
        # Apply main styling
        self.setStyleSheet("""
            EnhancedEditorPanel {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+N for new entry
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_entry_requested.emit)
        
        # Ctrl+S for manual save
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self._manual_save)
        
        # ESC to close
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.close_requested.emit)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Top bar connections
        self.top_bar.back_clicked.connect(self._on_back_clicked)
        self.top_bar.search_clicked.connect(self.search_requested.emit)
        self.top_bar.export_clicked.connect(self._on_export_clicked)
        self.top_bar.tags_clicked.connect(self._on_tags_clicked)
        self.top_bar.more_clicked.connect(self._on_more_clicked)
        self.top_bar.settings_clicked.connect(self.settings_requested.emit)
        self.top_bar.help_clicked.connect(self.help_requested.emit)
        
        # Text editor connections
        self.text_editor.content_changed.connect(self._on_content_changed)
        
        logger.debug("Signal connections established")
    
    def _on_content_changed(self, content: str):
        """Handle content changes for autosave."""
        self.content_changed.emit(content)
        
        # Start autosave timer
        self.autosave_timer.stop()
        delay = get_setting("autosave_debounce_ms", 900)
        self.autosave_timer.start(delay)
    
    def _autosave(self):
        """Perform autosave."""
        if not self.is_saving:
            self.is_saving = True
            self.status_bar.set_autosave_status(True)
            
            # Simulate save operation
            QTimer.singleShot(200, self._autosave_complete)
            
            logger.debug("Autosave triggered")
    
    def _autosave_complete(self):
        """Complete autosave operation."""
        self.is_saving = False
        self.status_bar.set_autosave_status(False)
        logger.debug("Autosave completed")
    
    def _manual_save(self):
        """Handle manual save (Ctrl+S)."""
        self.save_requested.emit()
        self._autosave()
        logger.info("Manual save requested")
    
    def _on_back_clicked(self):
        """Handle back/recent button click."""
        logger.info("Back/Recent clicked")
        # TODO: Implement recent entries functionality
    
    def _on_export_clicked(self):
        """Handle export button click."""
        logger.info("Export clicked")
        # TODO: Implement export functionality
    
    def _on_tags_clicked(self):
        """Handle tags button click."""
        logger.info("Tags clicked")
        # TODO: Implement tags functionality
    
    def _on_more_clicked(self):
        """Handle more actions button click."""
        logger.info("More actions clicked")
        # TODO: Implement more actions menu
    
    def get_content(self) -> str:
        """Get the current editor content."""
        return self.text_editor.toPlainText()
    
    def set_content(self, content: str):
        """Set the editor content."""
        self.text_editor.setPlainText(content)
    
    def clear_content(self):
        """Clear the editor content."""
        self.text_editor.clear()
    
    def focus_editor(self):
        """Focus the text editor."""
        self.text_editor.focus_editor()
    
    def update_settings(self):
        """Update UI based on current settings."""
        # Update font
        font_family = get_setting("font_family", "Segoe UI")
        font_size = get_setting("font_size", 11)
        font = QFont(font_family, font_size)
        self.text_editor.setFont(font)
        
        # Update easter egg visibility
        self.top_bar.update_egg_icon_visibility()
        
        logger.debug("Settings updated in editor panel")
    
    def show_and_focus(self):
        """Show the panel and focus the editor."""
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Focus editor after a short delay to ensure window is ready
        QTimer.singleShot(100, self.focus_editor)
        
        logger.debug("Editor panel shown and focused")
    
    def closeEvent(self, event):
        """Handle close event."""
        # Save content before closing
        if self.autosave_timer.isActive():
            self._autosave()
        
        event.accept()
        logger.debug("Editor panel closed")


# Convenience function for creating the enhanced editor panel
def create_enhanced_editor_panel(parent=None) -> EnhancedEditorPanel:
    """Create and configure an enhanced editor panel."""
    panel = EnhancedEditorPanel(parent)
    return panel