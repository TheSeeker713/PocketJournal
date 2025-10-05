"""
Integrated editor panel combining quick editor functionality with enhanced layout.

This module provides the primary note-taking interface with:
- Expandable panel functionality from QuickEditorPanel
- Enhanced layout with top bar and status bar from EnhancedEditorPanel
- All Step 5 requirements: minimalist top bar, clean text area, status strip
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QToolButton,
    QFrame, QSizePolicy, QApplication, QSpacerItem, QMessageBox
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QRect, QSize, QEasingCurve, QTimer, QPoint,
    Signal, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QTextCursor, QKeySequence, QShortcut, QIcon, QPixmap, 
    QPainter, QBrush, QColor, QPen, QKeyEvent, QMouseEvent
)

from ..settings import settings, get_setting, set_setting
from ..app_meta import APP_NAME
from ..core.autosave import AutosaveManager, EntryLifecycleManager
from ..core.smart_formatting import SmartFormatter, TitleSubtitleExtractor
from .formatting_toolbar import SmartFormattingToolbar
from .entry_actions import EntryActionsManager, open_data_folder

logger = logging.getLogger(__name__)


class IconButton(QToolButton):
    """Compact icon button for the top bar."""
    
    def __init__(self, icon_name: str, tooltip: str, size: int = 24, parent=None):
        super().__init__(parent)
        
        self.icon_name = icon_name
        self.setToolTip(tooltip)
        
        # Set size
        self.setFixedSize(size, size)
        
        # Create icon
        self.setIcon(self._create_icon())
        
        # Style the button
        self.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 4px;
                padding: 2px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
            }
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """)
    
    def _create_icon(self) -> QIcon:
        """Create a simple icon based on the icon name."""
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set color
        color = QColor(90, 90, 90)
        painter.setPen(QPen(color, 1.5))
        painter.setBrush(QBrush(color))
        
        # Draw different icons based on name
        center = size // 2
        
        if self.icon_name == "back":
            # Left arrow
            painter.drawLine(center + 2, center - 3, center - 1, center)
            painter.drawLine(center - 1, center, center + 2, center + 3)
            painter.drawLine(center - 1, center, center + 4, center)
            
        elif self.icon_name == "search":
            # Magnifying glass
            painter.drawEllipse(center - 3, center - 3, 5, 5)
            painter.drawLine(center + 1, center + 1, center + 3, center + 3)
            
        elif self.icon_name == "export":
            # Upload arrow
            painter.drawLine(center, center - 3, center, center + 2)
            painter.drawLine(center, center - 3, center - 2, center - 1)
            painter.drawLine(center, center - 3, center + 2, center - 1)
            painter.drawRect(center - 3, center + 1, 6, 1)
            
        elif self.icon_name == "tags":
            # Tag icon
            painter.drawRect(center - 3, center - 1, 4, 3)
            painter.drawLine(center + 1, center - 1, center + 3, center + 1)
            painter.drawLine(center + 3, center + 1, center + 1, center + 2)
            painter.drawEllipse(center - 1, center, 1, 1)
            
        elif self.icon_name == "more":
            # Three dots
            painter.drawEllipse(center - 4, center, 1, 1)
            painter.drawEllipse(center, center, 1, 1)
            painter.drawEllipse(center + 3, center, 1, 1)
            
        elif self.icon_name == "settings":
            # Gear icon (simplified)
            painter.drawEllipse(center - 2, center - 2, 4, 4)
            painter.drawEllipse(center - 1, center - 1, 2, 2)
            for i in range(6):
                angle = i * 60
                painter.save()
                painter.translate(center, center)
                painter.rotate(angle)
                painter.drawRect(0, -4, 1, 1)
                painter.restore()
                
        elif self.icon_name == "help":
            # Question mark
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")
            
        elif self.icon_name == "egg":
            # Easter egg icon
            painter.drawEllipse(center - 2, center - 3, 4, 6)
            painter.setPen(QPen(QColor(255, 200, 0), 1))
            painter.drawEllipse(center - 1, center - 1, 1, 1)
            
        else:
            # Default icon (square)
            painter.drawRect(center - 2, center - 2, 4, 4)
        
        painter.end()
        return QIcon(pixmap)


class CompactTopBar(QWidget):
    """Compact top bar with minimalist icons."""
    
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
        """Setup the compact top bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(2)
        
        # Left side icons
        self.back_btn = IconButton("back", "Back/Recent entries", 24)
        self.search_btn = IconButton("search", "Search entries (Ctrl+K)", 24)
        self.export_btn = IconButton("export", "Export entry", 24)
        self.tags_btn = IconButton("tags", "Manage tags", 24)
        self.more_btn = IconButton("more", "More entry actions", 24)
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.tags_btn)
        layout.addWidget(self.more_btn)
        
        # Spacer
        layout.addStretch()
        
        # Right side icons
        self.settings_btn = IconButton("settings", "Settings", 24)
        self.help_btn = IconButton("help", "Help (F1)", 24)
        
        # Easter egg icon (conditional)
        self.egg_btn = IconButton("egg", "Easter egg", 24)
        self.egg_btn.setVisible(get_setting("show_egg_icon", False))
        
        layout.addWidget(self.egg_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.help_btn)
        
        # Style the top bar
        self.setStyleSheet("""
            CompactTopBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
        """)
        
        self.setFixedHeight(30)
    
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
        """Update easter egg icon visibility."""
        show_egg = get_setting("show_egg_icon", False) or get_setting("eggs_enabled", True)
        self.egg_btn.setVisible(show_egg)


class CompactStatusBar(QWidget):
    """Compact status bar with autosave indicator and time."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 1, 6, 1)
        
        # Autosave status
        self.autosave_label = QLabel("●")
        self.autosave_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        self.autosave_label.setToolTip("Autosave active")
        
        # Spacer
        layout.addStretch()
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 9px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        layout.addWidget(self.autosave_label)
        layout.addWidget(self.time_label)
        
        # Style the status bar
        self.setStyleSheet("""
            CompactStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e9ecef;
            }
        """)
        
        self.setFixedHeight(18)
        self.update_time()
    
    def setup_timer(self):
        """Setup timer for updating time."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(30000)  # Update every 30 seconds
    
    def update_time(self):
        """Update time display in US format."""
        now = datetime.now()
        time_str = now.strftime("%m/%d/%Y %I:%M %p")
        self.time_label.setText(time_str)
    
    def set_autosave_status(self, saving: bool):
        """Update autosave status."""
        if saving:
            self.autosave_label.setText("⚬")
            self.autosave_label.setStyleSheet("""
                QLabel {
                    color: #ffc107;
                    font-weight: bold;
                    font-size: 10px;
                }
            """)
            self.autosave_label.setToolTip("Saving...")
        else:
            self.autosave_label.setText("●")
            self.autosave_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    font-size: 10px;
                }
            """)
            self.autosave_label.setToolTip("Autosave active")
    
    def set_last_save_time(self, save_time: str):
        """Update autosave tooltip with last save time."""
        if save_time:
            self.autosave_label.setToolTip(f"Last saved at {save_time}")
        else:
            self.autosave_label.setToolTip("Autosave active")


class IntegratedEditorPanel(QWidget):
    """
    Integrated editor panel combining expandable functionality with enhanced layout.
    
    Features from Step 5:
    - Top bar with tiny icons: Back/Recent, Search, Export, Tags, ⋯, Settings, Help, (Egg)
    - Main area: single plain text editor with padding, line-wrap, placeholder
    - Status strip: autosave indicator + local time in US format
    - Keyboard shortcuts: Ctrl+N (new), Ctrl+S (save), Ctrl+K (search), F1 (help)
    
    Plus expandable functionality:
    - Smooth expand/collapse animations
    - ESC key to close
    - Auto-save functionality
    """
    
    # Signals
    collapse_requested = Signal()
    content_changed = Signal(str)
    new_entry_requested = Signal()
    save_requested = Signal()
    search_requested = Signal()
    settings_requested = Signal()
    help_requested = Signal()
    
    # Entry lifecycle signals
    entry_created = Signal(dict)     # entry info
    entry_updated = Signal(dict)     # entry info
    entry_saved = Signal(str)        # save time
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Size configuration
        self.target_width = get_setting("editor_panel.width", 480)
        self.target_height = get_setting("editor_panel.height", 640)
        self.expanded_size = QSize(self.target_width, self.target_height)
        self.collapsed_size = QSize(48, 48)
        self.corner_position = "bottom_right"
        
        # Animation state
        self.expand_animation = None
        self.collapse_animation = None
        self.is_expanded = False
        
        # Initialize systems (will be set up after UI)
        self.autosave_manager = None
        self.lifecycle_manager = None
        self.smart_formatter = None
        self.title_subtitle_extractor = None
        self.entry_actions_manager = None
        self.current_toast = None  # For undo toasts
        
        # Setup UI and functionality
        self.setup_ui()
        self.setup_smart_formatting()
        self.setup_autosave_system()
        self.setup_entry_actions()
        self.setup_shortcuts()
        self.setup_connections()
        
        # Initial state
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.hide()
        
        logger.debug("Integrated editor panel initialized")
    
    def setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top bar
        self.top_bar = CompactTopBar()
        layout.addWidget(self.top_bar)
        
        # Formatting toolbar (will be initialized after text editor)
        self.formatting_toolbar = None
        self.formatting_toolbar_placeholder = QWidget()
        self.formatting_toolbar_placeholder.setFixedHeight(0)
        layout.addWidget(self.formatting_toolbar_placeholder)
        
        # Main text editor
        self.text_editor = QTextEdit()
        self.setup_text_editor()
        layout.addWidget(self.text_editor)
        
        # Status bar
        self.status_bar = CompactStatusBar()
        layout.addWidget(self.status_bar)
        
        # Apply styling
        self.setStyleSheet("""
            IntegratedEditorPanel {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
    
    def setup_text_editor(self):
        """Setup the main text editor."""
        # Placeholder text
        self.text_editor.setPlaceholderText("Start typing…")
        
        # Font configuration
        font_family = get_setting("font_family", "Segoe UI")
        font_size = get_setting("font_size", 11)
        # Ensure font_family is a string for testing
        if isinstance(font_family, int):
            font_family = "Segoe UI"
        font = QFont(font_family, font_size)
        self.text_editor.setFont(font)
        
        # Word wrap
        self.text_editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Styling with subtle padding
        self.text_editor.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #ffffff;
                padding: 8px;
                selection-background-color: #007acc;
                selection-color: white;
            }
        """)
        
        # Cursor width
        self.text_editor.setCursorWidth(2)
        
        # Size policy
        self.text_editor.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        
        # Connect content changes
        self.text_editor.textChanged.connect(self._on_text_changed)
    
    def setup_entry_actions(self):
        """Setup entry actions manager and toast display."""
        self.entry_actions_manager = EntryActionsManager()
        
        # Connect entry actions signals
        self.entry_actions_manager.entry_renamed.connect(self._on_entry_renamed)
        self.entry_actions_manager.entry_duplicated.connect(self._on_entry_duplicated)
        self.entry_actions_manager.entry_exported.connect(self._on_entry_exported)
        self.entry_actions_manager.entry_deleted.connect(self._on_entry_deleted)
        self.entry_actions_manager.entry_restored.connect(self._on_entry_restored)
        self.entry_actions_manager.show_toast.connect(self._show_toast)
        self.entry_actions_manager.hide_toast.connect(self._hide_toast)
    
    def _show_toast(self, toast_widget):
        """Show an undo toast at the bottom of the panel."""
        # Hide any existing toast
        self._hide_toast()
        
        self.current_toast = toast_widget
        toast_widget.setParent(self)
        
        # Position toast at the bottom of the panel
        panel_rect = self.geometry()
        toast_width = min(400, panel_rect.width() - 20)
        toast_height = 40
        
        toast_x = (panel_rect.width() - toast_width) // 2
        toast_y = panel_rect.height() - toast_height - 10
        
        toast_widget.setGeometry(toast_x, toast_y, toast_width, toast_height)
        toast_widget.show()
        toast_widget.raise_()
    
    def _hide_toast(self):
        """Hide the current toast."""
        if self.current_toast:
            self.current_toast.hide()
            self.current_toast.setParent(None)
            self.current_toast = None
    
    def _on_entry_renamed(self, old_path: str, new_path: str):
        """Handle entry renamed."""
        logger.info(f"Entry renamed: {old_path} -> {new_path}")
        # Update current entry path if it matches
        if (self.autosave_manager and self.autosave_manager.current_entry and 
            self.autosave_manager.current_entry.metadata.path == old_path):
            self.autosave_manager.current_entry.metadata.path = new_path
    
    def _on_entry_duplicated(self, new_path: str):
        """Handle entry duplicated."""
        logger.info(f"Entry duplicated: {new_path}")
        QMessageBox.information(self, "Entry Duplicated", f"Entry duplicated successfully!")
    
    def _on_entry_exported(self, source_path: str, destination: str):
        """Handle entry exported."""
        logger.info(f"Entry exported: {source_path} -> {destination}")
    
    def _on_entry_deleted(self, deleted_path: str):
        """Handle entry deleted."""
        logger.info(f"Entry deleted: {deleted_path}")
        # If current entry was deleted, create a new one
        if (self.autosave_manager and self.autosave_manager.current_entry and 
            self.autosave_manager.current_entry.metadata.path == deleted_path):
            self._create_new_entry()
    
    def _on_entry_restored(self, restored_path: str):
        """Handle entry restored."""
        logger.info(f"Entry restored: {restored_path}")
        QMessageBox.information(self, "Entry Restored", "Entry restored successfully!")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+N for new entry
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_entry_requested.emit)
        
        # Ctrl+S for manual save
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self._manual_save)
        
        # Ctrl+K for search
        search_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        search_shortcut.activated.connect(self.search_requested.emit)
        
        # F1 for help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.help_requested.emit)
        
        # ESC to close
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.collapse_requested.emit)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Top bar connections
        self.top_bar.back_clicked.connect(self._on_back_clicked)
        self.top_bar.search_clicked.connect(self._on_search_clicked)
        self.top_bar.export_clicked.connect(self._on_export_clicked)
        self.top_bar.tags_clicked.connect(self._on_tags_clicked)
        self.top_bar.more_clicked.connect(self._on_more_clicked)
        self.top_bar.settings_clicked.connect(self.settings_requested.emit)
        self.top_bar.help_clicked.connect(self.help_requested.emit)
        
        # Connect search requested signal to our search handler
        self.search_requested.connect(self._on_search_clicked)
    
    def setup_smart_formatting(self):
        """Setup smart formatting system."""
        # Initialize smart formatter
        self.smart_formatter = SmartFormatter(self.text_editor, self)
        
        # Initialize title/subtitle extractor
        self.title_subtitle_extractor = TitleSubtitleExtractor(self.smart_formatter, self)
        
        # Create and setup formatting toolbar
        self.formatting_toolbar = SmartFormattingToolbar(self.smart_formatter, self)
        
        # Replace placeholder with actual toolbar
        layout = self.layout()
        toolbar_index = layout.indexOf(self.formatting_toolbar_placeholder)
        layout.removeWidget(self.formatting_toolbar_placeholder)
        self.formatting_toolbar_placeholder.deleteLater()
        layout.insertWidget(toolbar_index, self.formatting_toolbar)
        
        # Connect title/subtitle changes to metadata updates
        self.title_subtitle_extractor.title_subtitle_changed.connect(self._on_title_subtitle_changed)
        
        # Connect formatting toolbar signals
        self.formatting_toolbar.rule_toggled.connect(self._on_formatting_rule_toggled)
        
        logger.debug("Smart formatting system initialized")
    
    def setup_autosave_system(self):
        """Setup autosave and entry lifecycle management."""
        # Initialize autosave manager
        self.autosave_manager = AutosaveManager(self.text_editor, self)
        
        # Initialize lifecycle manager
        self.lifecycle_manager = EntryLifecycleManager(self.autosave_manager, self)
        
        # Connect autosave signals to UI
        self.autosave_manager.save_started.connect(self._on_save_started)
        self.autosave_manager.save_completed.connect(self._on_save_completed)
        
        # Connect lifecycle signals to panel signals
        self.lifecycle_manager.entry_created.connect(self.entry_created.emit)
        self.lifecycle_manager.entry_updated.connect(self.entry_updated.emit)
        self.lifecycle_manager.entry_saved.connect(self.entry_saved.emit)
        self.lifecycle_manager.entry_saved.connect(self._update_save_time_display)
        
        # Connect panel signals to autosave actions
        self.new_entry_requested.connect(self._create_new_entry)
        self.save_requested.connect(self._manual_save)
        
        logger.debug("Autosave system initialized")
    
    def _on_text_changed(self):
        """Handle text changes - now managed by autosave system."""
        content = self.text_editor.toPlainText()
        self.content_changed.emit(content)
        # Note: Autosave manager handles the actual saving logic
    
    def _on_save_started(self):
        """Handle autosave start."""
        self.status_bar.set_autosave_status(True)
        logger.debug("Autosave started")
    
    def _on_save_completed(self, success: bool):
        """Handle autosave completion."""
        self.status_bar.set_autosave_status(False)
        if success:
            logger.debug("Autosave completed successfully")
        else:
            logger.warning("Autosave failed")
    
    def _update_save_time_display(self, save_time: str):
        """Update status bar with last save time."""
        self.status_bar.set_last_save_time(save_time)
    
    def _on_title_subtitle_changed(self, title: str, subtitle: str):
        """Handle title/subtitle changes from smart formatting."""
        # Update current entry metadata if available
        if self.autosave_manager and self.autosave_manager.current_entry:
            entry = self.autosave_manager.current_entry
            entry.metadata.title = title
            entry.metadata.subtitle = subtitle
            logger.debug(f"Title/subtitle updated: '{title}' / '{subtitle}'")
    
    def _on_formatting_rule_toggled(self, rule_name: str, enabled: bool):
        """Handle formatting rule toggle."""
        logger.info(f"Formatting rule '{rule_name}' {'enabled' if enabled else 'disabled'}")
    
    def _create_new_entry(self):
        """Create new entry via autosave manager."""
        if self.autosave_manager:
            self.autosave_manager.create_new_entry()
            logger.info("New entry created")
    
    def _manual_save(self):
        """Handle manual save via autosave manager."""
        self.save_requested.emit()
        if self.autosave_manager:
            success = self.autosave_manager.force_save()
            if success:
                logger.info("Manual save completed")
            else:
                logger.warning("Manual save failed")
    
    def _on_back_clicked(self):
        """Handle back button - show recent entries."""
        logger.info("Back/Recent clicked")
        
        # Show recent entries popover near the back button
        if not hasattr(self, '_recent_popover'):
            from .recent_and_search import RecentEntriesPopover
            self._recent_popover = RecentEntriesPopover(self)
            self._recent_popover.entry_selected.connect(self._on_search_entry_selected)
        
        # Position popover near back button
        back_btn_pos = self.top_bar.back_btn.mapToGlobal(QPoint(0, 0))
        back_btn_size = self.top_bar.back_btn.size()
        
        # Show below the button
        popover_pos = QPoint(
            back_btn_pos.x(),
            back_btn_pos.y() + back_btn_size.height() + 5
        )
        
        self._recent_popover.move(popover_pos)
        self._recent_popover.load_recent_entries()
        self._recent_popover.show()
        self._recent_popover.raise_()
    
    def _on_search_clicked(self):
        """Handle search button or Ctrl+K shortcut."""
        logger.info("Search clicked")
        
        # Show search dialog
        if not hasattr(self, '_search_dialog'):
            from .recent_and_search import SearchDialog
            self._search_dialog = SearchDialog(self)
            self._search_dialog.entry_selected.connect(self._on_search_entry_selected)
        
        self._search_dialog.show()
        self._search_dialog.raise_()
        self._search_dialog.activateWindow()
        
    def _on_search_entry_selected(self, file_path: str):
        """Handle search entry selection."""
        logger.info(f"Loading entry from search: {file_path}")
        
        # Load the selected entry
        if self.autosave_manager:
            try:
                # Load the entry
                entry_manager = self.autosave_manager.entry_manager
                entry = entry_manager.load_entry(file_path)
                
                if entry:
                    # Set as current entry
                    self.autosave_manager.current_entry = entry
                    
                    # Update editor content
                    self.text_editor.setPlainText(entry.content)
                    
                    # Move cursor to end
                    cursor = self.text_editor.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.text_editor.setTextCursor(cursor)
                    
                    # Focus editor
                    self.text_editor.setFocus()
                    
                    logger.info(f"Loaded entry: {entry.metadata.title}")
                else:
                    QMessageBox.warning(self, "Load Error", 
                                      "Could not load the selected entry.")
            except Exception as e:
                logger.error(f"Error loading entry: {e}")
                QMessageBox.critical(self, "Error", 
                                   f"Error loading entry: {str(e)}")
    
    def _on_export_clicked(self):
        """Handle export button."""
        logger.info("Export clicked")
    
    def _on_tags_clicked(self):
        """Handle tags button."""
        logger.info("Tags clicked")
    
    def _on_more_clicked(self):
        """Handle more actions button - show entry actions menu."""
        logger.info("More actions clicked")
        
        # Check if we have a current entry
        if not (self.autosave_manager and self.autosave_manager.current_entry):
            QMessageBox.information(self, "No Entry", 
                                  "No entry is currently loaded. Please create or open an entry first.")
            return
        
        current_entry = self.autosave_manager.current_entry
        
        # Ensure entry has been saved (has a path)
        if not current_entry.metadata.path:
            # Force save first
            success = self.autosave_manager.force_save()
            if not success:
                QMessageBox.warning(self, "Save Required", 
                                  "Please save the entry before accessing more actions.")
                return
        
        # Create and show the entry actions menu
        menu = self.entry_actions_manager.create_actions_menu(current_entry, self)
        
        # Position menu relative to the more button
        button_rect = self.top_bar.more_btn.geometry()
        button_global_pos = self.top_bar.more_btn.mapToGlobal(button_rect.bottomLeft())
        
        menu.exec(button_global_pos)
    
    def expand_from_position(self, start_pos, start_size):
        """Expand the panel from a given position."""
        if self.is_expanded:
            return
        
        # Calculate target position based on corner
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        if self.corner_position == "bottom_right":
            target_x = screen_geometry.right() - self.target_width - 20
            target_y = screen_geometry.bottom() - self.target_height - 20
        elif self.corner_position == "bottom_left":
            target_x = screen_geometry.left() + 20
            target_y = screen_geometry.bottom() - self.target_height - 20
        elif self.corner_position == "top_right":
            target_x = screen_geometry.right() - self.target_width - 20
            target_y = screen_geometry.top() + 20
        else:  # top_left
            target_x = screen_geometry.left() + 20
            target_y = screen_geometry.top() + 20
        
        # Set initial position and size
        start_rect = QRect(start_pos.x(), start_pos.y(), start_size.width(), start_size.height())
        target_rect = QRect(target_x, target_y, self.target_width, self.target_height)
        
        self.setGeometry(start_rect)
        self.show()
        
        # Create expand animation
        self.expand_animation = QPropertyAnimation(self, b"geometry")
        self.expand_animation.setDuration(300)
        self.expand_animation.setStartValue(start_rect)
        self.expand_animation.setEndValue(target_rect)
        self.expand_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.expand_animation.finished.connect(self._on_expand_finished)
        
        self.expand_animation.start()
        logger.debug("Panel expand animation started")
    
    def collapse_to_position(self, target_pos, target_size):
        """Collapse the panel to a given position."""
        if not self.is_expanded:
            return
        
        current_rect = self.geometry()
        target_rect = QRect(target_pos.x(), target_pos.y(), target_size.width(), target_size.height())
        
        # Create collapse animation
        self.collapse_animation = QPropertyAnimation(self, b"geometry")
        self.collapse_animation.setDuration(300)
        self.collapse_animation.setStartValue(current_rect)
        self.collapse_animation.setEndValue(target_rect)
        self.collapse_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.collapse_animation.finished.connect(self._on_collapse_finished)
        
        self.collapse_animation.start()
        logger.debug("Panel collapse animation started")
    
    def _on_expand_finished(self):
        """Handle expand animation completion."""
        self.is_expanded = True
        self._focus_editor()
        logger.debug("Panel expand completed")
    
    def _on_collapse_finished(self):
        """Handle collapse animation completion."""
        self.is_expanded = False
        self.hide()
        logger.debug("Panel collapse completed")
    
    def _focus_editor(self):
        """Focus the text editor."""
        self.text_editor.setFocus()
        cursor = self.text_editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_editor.setTextCursor(cursor)
    
    def get_content(self) -> str:
        """Get editor content."""
        return self.text_editor.toPlainText()
    
    def set_content(self, content: str):
        """Set editor content."""
        self.text_editor.setPlainText(content)
    
    def clear_content(self):
        """Clear editor content."""
        self.text_editor.clear()
    
    def save_content(self):
        """Save current content (trigger autosave)."""
        if self.autosave_manager:
            self.autosave_manager.force_save()
    
    def save_settings(self):
        """Save panel settings."""
        # Save corner position and size
        settings.set("editor_panel.corner_position", self.corner_position)
        settings.set("editor_panel.width", self.target_width)
        settings.set("editor_panel.height", self.target_height)
    
    def load_settings(self):
        """Load panel settings."""
        self.corner_position = get_setting("editor_panel.corner_position", "bottom_right")
        self.target_width = get_setting("editor_panel.width", 480)
        self.target_height = get_setting("editor_panel.height", 640)
        self.expanded_size = QSize(self.target_width, self.target_height)
    
    def update_settings(self):
        """Update UI based on settings."""
        # Update font
        font_family = get_setting("font_family", "Segoe UI")
        font_size = get_setting("font_size", 11)
        font = QFont(font_family, font_size)
        self.text_editor.setFont(font)
        
        # Update easter egg visibility
        self.top_bar.update_egg_icon_visibility()
        
        logger.debug("Editor panel settings updated")
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        # Let the text editor handle most key events
        if self.text_editor.hasFocus():
            super().keyPressEvent(event)
        else:
            # If no widget has focus, focus the editor
            self._focus_editor()
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        # Focus the editor when clicking in the panel
        if not self.text_editor.hasFocus():
            self._focus_editor()
        super().mousePressEvent(event)
    
    # Entry management methods
    def get_current_entry_info(self) -> dict:
        """Get current entry information."""
        if self.autosave_manager:
            return self.autosave_manager.get_current_entry_info()
        return {}
    
    def load_entry(self, file_path: str) -> bool:
        """Load entry from file."""
        if self.autosave_manager:
            return self.autosave_manager.load_entry(file_path)
        return False
    
    def save_and_close(self) -> bool:
        """Save current entry before closing."""
        if self.autosave_manager:
            return self.autosave_manager.save_and_close()
        return True
    
    def get_last_save_time(self) -> str:
        """Get last save time for status display."""
        if self.autosave_manager:
            return self.autosave_manager.get_last_save_time_local()
        return ""
    
    def update_autosave_settings(self):
        """Update autosave settings."""
        if self.autosave_manager:
            self.autosave_manager.update_settings()
    
    # Smart formatting methods
    def get_current_title_subtitle(self) -> tuple:
        """Get current parsed title and subtitle."""
        if self.title_subtitle_extractor:
            return self.title_subtitle_extractor.get_current_title_subtitle()
        return "", ""
    
    def toggle_formatting_rule(self, rule_name: str) -> bool:
        """Toggle a specific formatting rule."""
        if self.smart_formatter:
            return self.smart_formatter.toggle_rule(rule_name)
        return False
    
    def get_formatting_rules_info(self) -> dict:
        """Get information about all formatting rules."""
        if self.smart_formatter:
            return self.smart_formatter.get_rules_info()
        return {}
    
    def enable_all_formatting(self):
        """Enable all formatting rules."""
        if self.smart_formatter:
            self.smart_formatter.enable_all_rules()
            if self.formatting_toolbar:
                self.formatting_toolbar.update_button_states()
    
    def disable_all_formatting(self):
        """Disable all formatting rules."""
        if self.smart_formatter:
            self.smart_formatter.disable_all_rules()
            if self.formatting_toolbar:
                self.formatting_toolbar.update_button_states()
    
    def apply_formatting(self):
        """Manually trigger formatting application."""
        if self.smart_formatter:
            self.smart_formatter.apply_formatting()