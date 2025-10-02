"""
Expandable editor panel that shows when the micro-launcher is activated.

This panel provides a compact but functional text editor for quick note-taking.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QToolButton, QFrame, QApplication
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QRect, QSize, QEasingCurve, QTimer, QPoint,
    Signal, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QTextDocument, QIcon, QKeyEvent, QMouseEvent
)

from ..settings import settings


class QuickEditorPanel(QWidget):
    """
    Expandable editor panel for quick note-taking.
    
    Features:
    - Compact text editor
    - Auto-save functionality
    - Expand/collapse animations
    - ESC key to close
    - Click-outside-to-close
    """
    
    # Signals
    collapse_requested = Signal()
    content_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration
        self.expanded_size = QSize(480, 640)
        self.collapsed_size = QSize(48, 48)
        self.corner_position = "top-right"
        
        # Load settings
        self.load_settings()
        
        # Setup auto-save first (before UI setup)
        self.setup_autosave()
        
        # Setup window properties
        self.setup_window()
        
        # Setup UI
        self.setup_ui()
        
        # Initially collapsed
        self.is_expanded = False
        self.setFixedSize(self.collapsed_size)
    
    def setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
        """)
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header with close button
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # Text editor
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont(settings.get("font_family", "Segoe UI"), 
                                     settings.get("font_size", 11)))
        self.text_editor.setPlaceholderText("Start writing your thoughts...")
        self.text_editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_editor)
        
        # Footer with status
        self.footer = self.create_footer()
        layout.addWidget(self.footer)
        
        # Load content
        self.load_content()
    
    def create_header(self):
        """Create the header with title and close button."""
        header = QFrame()
        header.setFixedHeight(32)
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #e9ecef;
                border-radius: 0;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Title
        title = QLabel("Quick Notes")
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #495057; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Close button (circle icon)
        self.close_button = QToolButton()
        self.close_button.setText("●")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QToolButton {
                background-color: #45a049;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #4CAF50;
            }
            QToolButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.close_button.clicked.connect(self.collapse_requested.emit)
        layout.addWidget(self.close_button)
        
        return header
    
    def create_footer(self):
        """Create the footer with status information."""
        footer = QFrame()
        footer.setFixedHeight(24)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
                border-top: 1px solid #e9ecef;
                border-radius: 0;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 2, 8, 2)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setStyleSheet("color: #6c757d; background: transparent; border: none;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Word count
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setFont(QFont("Segoe UI", 8))
        self.word_count_label.setStyleSheet("color: #6c757d; background: transparent; border: none;")
        layout.addWidget(self.word_count_label)
        
        return footer
    
    def setup_autosave(self):
        """Setup auto-save functionality."""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.save_content)
        self.autosave_timer.setSingleShot(True)
        
        # Get debounce time from settings
        self.autosave_debounce = settings.get("autosave_debounce_ms", 900)
    
    def load_settings(self):
        """Load panel settings."""
        self.expanded_size = QSize(
            settings.get("editor_panel.width", 480),
            settings.get("editor_panel.height", 640)
        )
        self.corner_position = settings.get("launcher.last_corner", "top-right")
    
    def save_settings(self):
        """Save current panel settings."""
        settings.set("editor_panel.width", self.expanded_size.width())
        settings.set("editor_panel.height", self.expanded_size.height())
    
    def load_content(self):
        """Load the last saved content."""
        content = settings.get("quick_notes.content", "")
        if content:
            self.text_editor.setPlainText(content)
    
    def save_content(self):
        """Save the current content."""
        content = self.text_editor.toPlainText()
        settings.set("quick_notes.content", content)
        self.status_label.setText("Saved")
        
        # Clear status after a moment
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    def on_text_changed(self):
        """Handle text changes."""
        # Update word count
        text = self.text_editor.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        self.word_count_label.setText(f"{word_count} words")
        
        # Restart autosave timer
        self.autosave_timer.stop()
        self.autosave_timer.start(self.autosave_debounce)
        
        # Update status
        self.status_label.setText("Modified")
        
        # Emit content changed signal
        self.content_changed.emit(text)
    
    def expand_from_position(self, source_pos, source_size):
        """Expand the panel from the given position with animation."""
        if self.is_expanded:
            return
        
        # Calculate target position based on corner
        target_pos = self.calculate_expanded_position(source_pos)
        
        # Set initial state (collapsed)
        self.setFixedSize(source_size)
        self.move(source_pos)
        self.show()
        
        # Create animations
        self.expand_animation_group = QParallelAnimationGroup()
        
        # Size animation
        size_animation = QPropertyAnimation(self, b"size")
        size_animation.setDuration(300)
        size_animation.setStartValue(source_size)
        size_animation.setEndValue(self.expanded_size)
        size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Position animation
        pos_animation = QPropertyAnimation(self, b"pos")
        pos_animation.setDuration(300)
        pos_animation.setStartValue(source_pos)
        pos_animation.setEndValue(target_pos)
        pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Add animations to group
        self.expand_animation_group.addAnimation(size_animation)
        self.expand_animation_group.addAnimation(pos_animation)
        
        # Connect finished signal
        self.expand_animation_group.finished.connect(self.on_expand_finished)
        
        # Start animation
        self.expand_animation_group.start()
        
        self.is_expanded = True
    
    def collapse_to_position(self, target_pos, target_size):
        """Collapse the panel to the given position with animation."""
        if not self.is_expanded:
            return
        
        # Save content before collapsing
        self.save_content()
        
        # Create animations
        self.collapse_animation_group = QParallelAnimationGroup()
        
        # Size animation
        size_animation = QPropertyAnimation(self, b"size")
        size_animation.setDuration(250)
        size_animation.setStartValue(self.size())
        size_animation.setEndValue(target_size)
        size_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Position animation
        pos_animation = QPropertyAnimation(self, b"pos")
        pos_animation.setDuration(250)
        pos_animation.setStartValue(self.pos())
        pos_animation.setEndValue(target_pos)
        pos_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Add animations to group
        self.collapse_animation_group.addAnimation(size_animation)
        self.collapse_animation_group.addAnimation(pos_animation)
        
        # Connect finished signal
        self.collapse_animation_group.finished.connect(self.on_collapse_finished)
        
        # Start animation
        self.collapse_animation_group.start()
        
        self.is_expanded = False
    
    def calculate_expanded_position(self, launcher_pos):
        """Calculate where the expanded panel should be positioned."""
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        
        # Position based on corner
        if self.corner_position == "top-left":
            x = margin
            y = margin
        elif self.corner_position == "top-right":
            x = screen.width() - self.expanded_size.width() - margin
            y = margin
        elif self.corner_position == "bottom-left":
            x = margin
            y = screen.height() - self.expanded_size.height() - margin
        else:  # bottom-right
            x = screen.width() - self.expanded_size.width() - margin
            y = screen.height() - self.expanded_size.height() - margin
        
        return QPoint(x, y)
    
    def on_expand_finished(self):
        """Called when expand animation finishes."""
        # Focus the text editor
        self.text_editor.setFocus()
        
        # Position cursor at end
        cursor = self.text_editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_editor.setTextCursor(cursor)
    
    def on_collapse_finished(self):
        """Called when collapse animation finishes."""
        # Hide the panel
        self.hide()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            # ESC key closes the panel
            self.collapse_requested.emit()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus out events."""
        # Note: We don't auto-close on focus loss as it can be annoying
        # User can still close with ESC or the close button
        super().focusOutEvent(event)