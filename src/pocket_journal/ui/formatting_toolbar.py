"""
Formatting toggle buttons for the smart formatting toolbar.
Provides inline toggles to disable specific formatting rules.
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QToolButton, QLabel, QFrame, 
    QSizePolicy, QSpacerItem, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QPen

from ..core.smart_formatting import SmartFormatter, FormattingToggleManager


class FormattingToggleButton(QToolButton):
    """Custom toggle button for formatting rules."""
    
    def __init__(self, rule_name: str, description: str, icon_type: str = "text", parent=None):
        super().__init__(parent)
        
        self.rule_name = rule_name
        self.description = description
        self.icon_type = icon_type
        
        # Setup button
        self.setCheckable(True)
        self.setChecked(True)  # Default enabled
        self.setFixedSize(20, 20)
        self.setToolTip(f"{description} (Click to toggle)")
        
        # Create icon
        self.setIcon(self._create_icon())
        
        # Style
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f9fa;
                padding: 1px;
            }
            QToolButton:checked {
                background-color: #007acc;
                border-color: #0056b3;
                color: white;
            }
            QToolButton:hover {
                border-color: #007acc;
            }
            QToolButton:pressed {
                background-color: #0056b3;
            }
        """)
    
    def _create_icon(self) -> QIcon:
        """Create icon based on formatting type."""
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set color based on checked state
        color = QColor(255, 255, 255) if self.isChecked() else QColor(70, 70, 70)
        painter.setPen(QPen(color, 1))
        
        font = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(font)
        
        center_x = size // 2
        center_y = size // 2
        
        if self.icon_type == "bold":
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "B")
            
        elif self.icon_type == "italic":
            painter.setFont(QFont("Arial", 9, QFont.Weight.Normal))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "I")
            
        elif self.icon_type == "underline":
            painter.drawText(center_x - 4, center_y - 1, "U")
            painter.drawLine(center_x - 4, center_y + 3, center_x + 4, center_y + 3)
            
        elif self.icon_type == "list":
            # Draw bullet points
            painter.drawEllipse(2, 3, 2, 2)
            painter.drawLine(6, 4, 13, 4)
            painter.drawEllipse(2, 7, 2, 2)
            painter.drawLine(6, 8, 13, 8)
            painter.drawEllipse(2, 11, 2, 2)
            painter.drawLine(6, 12, 13, 12)
            
        elif self.icon_type == "caps":
            painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "ABC")
            
        elif self.icon_type == "exclamation":
            painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "!")
            
        elif self.icon_type == "parentheses":
            painter.setFont(QFont("Arial", 10))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "()")
            
        elif self.icon_type == "note":
            painter.setFont(QFont("Arial", 6, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NOTE")
            
        else:  # default text icon
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F")
        
        painter.end()
        return QIcon(pixmap)
    
    def setChecked(self, checked: bool):
        """Override to update icon when state changes."""
        super().setChecked(checked)
        self.setIcon(self._create_icon())


class SmartFormattingToolbar(QWidget):
    """Toolbar with toggles for smart formatting rules."""
    
    # Signals
    rule_toggled = Signal(str, bool)  # rule_name, enabled
    all_rules_disabled = Signal()
    all_rules_enabled = Signal()
    
    def __init__(self, smart_formatter: SmartFormatter, parent=None):
        """Initialize smart formatting toolbar."""
        super().__init__(parent)
        
        self.smart_formatter = smart_formatter
        self.toggle_manager = FormattingToggleManager(smart_formatter, self)
        self.toggle_buttons: Dict[str, FormattingToggleButton] = {}
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the toolbar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)
        
        # Label
        label = QLabel("Format:")
        label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 9px;
                font-weight: bold;
            }
        """)
        layout.addWidget(label)
        
        # Create toggle buttons for main formatting rules
        button_configs = [
            ("all_caps", "Bold ALL-CAPS words", "caps"),
            ("emphatic_exclamation", "Bold phrases with !", "exclamation"),
            ("parentheticals", "Italics for parentheticals", "parentheses"),
            ("note_lines", "Underline NOTE: lines", "note"),
            ("bullet_lists", "Format bullet lists", "list"),
        ]
        
        for rule_name, description, icon_type in button_configs:
            if rule_name in self.smart_formatter.rules:
                button = FormattingToggleButton(rule_name, description, icon_type)
                self.toggle_buttons[rule_name] = button
                layout.addWidget(button)
                
                # Register with toggle manager
                self.toggle_manager.register_toggle_button(rule_name, button)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #ccc;")
        layout.addWidget(separator)
        
        # All/None buttons
        self.all_button = QToolButton()
        self.all_button.setText("All")
        self.all_button.setFixedSize(24, 20)
        self.all_button.setToolTip("Enable all formatting rules")
        self.all_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f9fa;
                font-size: 8px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #e9ecef;
                border-color: #007acc;
            }
            QToolButton:pressed {
                background-color: #dee2e6;
            }
        """)
        layout.addWidget(self.all_button)
        
        self.none_button = QToolButton()
        self.none_button.setText("None")
        self.none_button.setFixedSize(24, 20)
        self.none_button.setToolTip("Disable all formatting rules")
        self.none_button.setStyleSheet(self.all_button.styleSheet())
        layout.addWidget(self.none_button)
        
        # Spacer
        layout.addStretch()
        
        # Style the toolbar
        self.setStyleSheet("""
            SmartFormattingToolbar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
        """)
        
        self.setFixedHeight(24)
    
    def setup_connections(self):
        """Setup signal connections."""
        # All/None buttons
        self.all_button.clicked.connect(self._enable_all_rules)
        self.none_button.clicked.connect(self._disable_all_rules)
        
        # Connect toggle manager signals
        self.toggle_manager.rule_toggled.connect(self.rule_toggled.emit)
    
    def _enable_all_rules(self):
        """Enable all formatting rules."""
        self.smart_formatter.enable_all_rules()
        self.toggle_manager.update_button_states()
        self.all_rules_enabled.emit()
    
    def _disable_all_rules(self):
        """Disable all formatting rules."""
        self.smart_formatter.disable_all_rules()
        self.toggle_manager.update_button_states()
        self.all_rules_disabled.emit()
    
    def update_button_states(self):
        """Update all button states."""
        self.toggle_manager.update_button_states()
    
    def get_enabled_rules(self) -> Dict[str, bool]:
        """Get current state of all formatting rules."""
        return {
            rule_name: button.isChecked() 
            for rule_name, button in self.toggle_buttons.items()
        }


class CompactFormattingToolbar(QWidget):
    """Compact version of formatting toolbar for minimal space."""
    
    # Signals  
    rule_toggled = Signal(str, bool)
    
    def __init__(self, smart_formatter: SmartFormatter, parent=None):
        """Initialize compact formatting toolbar."""
        super().__init__(parent)
        
        self.smart_formatter = smart_formatter
        self.toggle_manager = FormattingToggleManager(smart_formatter, self)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup compact toolbar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(1)
        
        # Just the most important formatting toggles
        essential_rules = [
            ("all_caps", "Bold ALL-CAPS", "caps"),
            ("parentheticals", "Italics (text)", "parentheses"),
            ("bullet_lists", "Format lists", "list"),
        ]
        
        for rule_name, description, icon_type in essential_rules:
            if rule_name in self.smart_formatter.rules:
                button = FormattingToggleButton(rule_name, description, icon_type)
                button.setFixedSize(16, 16)
                layout.addWidget(button)
                
                # Register with toggle manager
                self.toggle_manager.register_toggle_button(rule_name, button)
        
        # Style
        self.setStyleSheet("""
            CompactFormattingToolbar {
                background-color: rgba(248, 249, 250, 0.8);
            }
        """)
        
        self.setFixedHeight(18)