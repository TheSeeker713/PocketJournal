"""
Smart formatting system for PocketJournal.
Applies display-time formatting rules without mutating raw text.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextDocument, QTextCursor, QTextCharFormat, QFont, QColor
from PySide6.QtWidgets import QTextEdit

from ..settings import get_setting, set_setting


@dataclass
class FormatRule:
    """Represents a formatting rule with pattern and style."""
    name: str
    pattern: str
    format_type: str  # 'bold', 'italic', 'underline', 'color'
    enabled: bool = True
    description: str = ""


class SmartFormatter(QObject):
    """Handles smart formatting of text without mutating raw content."""
    
    # Signals
    formatting_changed = Signal()
    rules_updated = Signal()
    
    def __init__(self, text_editor: QTextEdit, parent=None):
        """Initialize smart formatter."""
        super().__init__(parent)
        
        self.text_editor = text_editor
        self.original_text = ""
        self.title = ""
        self.subtitle = ""
        self._formatting_in_progress = False  # Guard against infinite loops
        
        # Formatting rules
        self.rules = {
            'all_caps': FormatRule(
                name='all_caps',
                pattern=r'\b[A-Z]{4,}\b',
                format_type='bold',
                description='Bold ALL-CAPS words (≥4 chars)'
            ),
            'emphatic_exclamation': FormatRule(
                name='emphatic_exclamation',
                pattern=r'[^.!?]*!',
                format_type='bold',
                description='Bold emphatic phrases ending in "!"'
            ),
            'important_phrases': FormatRule(
                name='important_phrases',
                pattern=r'IMPORTANT:[^.!?]*[.!?]',
                format_type='bold',
                description='Bold phrases following "IMPORTANT:"'
            ),
            'parentheticals': FormatRule(
                name='parentheticals',
                pattern=r'\([^)]*\)',
                format_type='italic',
                description='Italics for parentheticals ( … )'
            ),
            'note_lines': FormatRule(
                name='note_lines',
                pattern=r'^NOTE:.*$',
                format_type='underline',
                description='Underline lines starting with "NOTE:"'
            ),
            'action_lines': FormatRule(
                name='action_lines',
                pattern=r'^ACTION:.*$',
                format_type='underline',
                description='Underline lines starting with "ACTION:"'
            ),
            'bullet_lists': FormatRule(
                name='bullet_lists',
                pattern=r'^[-*]\s+.*$',
                format_type='list',
                description='Format bullet lists (-, *)'
            ),
            'numbered_lists': FormatRule(
                name='numbered_lists',
                pattern=r'^\d+\.\s+.*$',
                format_type='list',
                description='Format numbered lists (1.)'
            )
        }
        
        # Load settings
        self.load_rule_settings()
        
        # Connect to text changes
        self.text_editor.textChanged.connect(self._on_text_changed)
    
    def load_rule_settings(self):
        """Load rule enabled/disabled state from settings."""
        for rule_name, rule in self.rules.items():
            enabled = get_setting(f"formatting.{rule_name}.enabled", True)
            rule.enabled = enabled
    
    def save_rule_settings(self):
        """Save rule enabled/disabled state to settings."""
        for rule_name, rule in self.rules.items():
            set_setting(f"formatting.{rule_name}.enabled", rule.enabled)
    
    def toggle_rule(self, rule_name: str) -> bool:
        """Toggle a formatting rule on/off."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = not self.rules[rule_name].enabled
            self.save_rule_settings()
            self.apply_formatting()
            self.rules_updated.emit()
            return self.rules[rule_name].enabled
        return False
    
    def get_rule_state(self, rule_name: str) -> bool:
        """Get current state of a formatting rule."""
        return self.rules.get(rule_name, FormatRule("", "", "")).enabled
    
    def parse_title_subtitle(self, text: str) -> Tuple[str, str]:
        """Parse first two sentences for title and subtitle."""
        if not text.strip():
            return "", ""
        
        # Handle markdown headers specially
        lines = text.split('\n')
        first_line = lines[0].strip()
        
        # Check if first line is a markdown header
        if first_line.startswith('#'):
            title = re.sub(r'^#+\s*', '', first_line).strip()
            # Look for subtitle in remaining content
            remaining_text = '\n'.join(lines[1:]).strip()
            if remaining_text:
                # Split remaining text into sentences (preserve punctuation)
                sentences = re.split(r'(?<=[.!?])\s+', remaining_text)
                sentences = [s.strip() for s in sentences if s.strip()]
                subtitle = sentences[0][:200] if sentences else ""
            else:
                subtitle = ""
        else:
            # No markdown header, split by sentences (preserve punctuation)
            clean_text = text.strip()
            sentences = re.split(r'(?<=[.!?])\s+', clean_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            title = sentences[0][:100] if sentences else ""
            subtitle = sentences[1][:200] if len(sentences) >= 2 else ""
        
        return title, subtitle
    
    def _on_text_changed(self):
        """Handle text changes and update formatting."""
        # Guard against infinite loops during formatting
        if self._formatting_in_progress:
            return
            
        current_text = self.text_editor.toPlainText()
        
        # Update title/subtitle
        self.title, self.subtitle = self.parse_title_subtitle(current_text)
        
        # Store original text
        self.original_text = current_text
        
        # Apply formatting
        self.apply_formatting()
        
        self.formatting_changed.emit()
    
    def apply_formatting(self):
        """Apply all enabled formatting rules to the text."""
        if not self.original_text or self._formatting_in_progress:
            return
        
        # Set guard flag
        self._formatting_in_progress = True
        
        try:
            # Get current cursor position to restore later
            cursor = self.text_editor.textCursor()
            cursor_position = cursor.position()
            
            # Clear existing formatting
            self.clear_formatting()
            
            # Apply each enabled rule
            for rule in self.rules.values():
                if rule.enabled:
                    self._apply_rule(rule)
            
            # Restore cursor position
            cursor.setPosition(cursor_position)
            self.text_editor.setTextCursor(cursor)
        finally:
            # Always clear guard flag
            self._formatting_in_progress = False
    
    def clear_formatting(self):
        """Clear all formatting from the text editor."""
        cursor = self.text_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        # Reset to default format
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)
        
        cursor.clearSelection()
        self.text_editor.setTextCursor(cursor)
    
    def _apply_rule(self, rule: FormatRule):
        """Apply a specific formatting rule."""
        text = self.original_text
        pattern_flags = re.MULTILINE if rule.name in ['note_lines', 'action_lines', 'bullet_lists', 'numbered_lists'] else 0
        
        try:
            matches = list(re.finditer(rule.pattern, text, pattern_flags))
            
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                
                # Create cursor and select the match
                cursor = self.text_editor.textCursor()
                cursor.setPosition(start_pos)
                cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
                
                # Apply formatting based on rule type
                char_format = QTextCharFormat()
                
                if rule.format_type == 'bold':
                    char_format.setFontWeight(QFont.Weight.Bold)
                elif rule.format_type == 'italic':
                    char_format.setFontItalic(True)
                elif rule.format_type == 'underline':
                    char_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
                elif rule.format_type == 'list':
                    # For lists, apply bold and slight color change
                    char_format.setFontWeight(QFont.Weight.Bold)
                    char_format.setForeground(QColor(70, 130, 180))  # Steel blue
                
                cursor.setCharFormat(char_format)
                
        except re.error as e:
            print(f"Error applying rule {rule.name}: {e}")
    
    def get_current_title_subtitle(self) -> Tuple[str, str]:
        """Get current parsed title and subtitle."""
        return self.title, self.subtitle
    
    def disable_all_rules(self):
        """Disable all formatting rules."""
        for rule in self.rules.values():
            rule.enabled = False
        self.save_rule_settings()
        self.clear_formatting()
        self.rules_updated.emit()
    
    def enable_all_rules(self):
        """Enable all formatting rules."""
        for rule in self.rules.values():
            rule.enabled = True
        self.save_rule_settings()
        self.apply_formatting()
        self.rules_updated.emit()
    
    def get_rules_info(self) -> Dict[str, Dict]:
        """Get information about all formatting rules."""
        return {
            name: {
                'name': rule.name,
                'description': rule.description,
                'enabled': rule.enabled,
                'format_type': rule.format_type
            }
            for name, rule in self.rules.items()
        }


class FormattingToggleManager(QObject):
    """Manages formatting toggle buttons and state."""
    
    # Signals
    rule_toggled = Signal(str, bool)  # rule_name, enabled
    
    def __init__(self, smart_formatter: SmartFormatter, parent=None):
        """Initialize formatting toggle manager."""
        super().__init__(parent)
        
        self.smart_formatter = smart_formatter
        self.toggle_buttons = {}
        
        # Connect to formatter signals
        self.smart_formatter.rules_updated.connect(self._on_rules_updated)
    
    def register_toggle_button(self, rule_name: str, button):
        """Register a toggle button for a formatting rule."""
        self.toggle_buttons[rule_name] = button
        
        # Set initial state
        enabled = self.smart_formatter.get_rule_state(rule_name)
        button.setChecked(enabled)
        
        # Connect button to toggle function
        button.toggled.connect(lambda checked: self._toggle_rule(rule_name, checked))
    
    def _toggle_rule(self, rule_name: str, enabled: bool):
        """Handle rule toggle from button."""
        if rule_name in self.smart_formatter.rules:
            self.smart_formatter.rules[rule_name].enabled = enabled
            self.smart_formatter.save_rule_settings()
            self.smart_formatter.apply_formatting()
            self.rule_toggled.emit(rule_name, enabled)
    
    def _on_rules_updated(self):
        """Handle rules updated from formatter."""
        for rule_name, button in self.toggle_buttons.items():
            enabled = self.smart_formatter.get_rule_state(rule_name)
            button.setChecked(enabled)
    
    def update_button_states(self):
        """Update all toggle button states."""
        for rule_name, button in self.toggle_buttons.items():
            enabled = self.smart_formatter.get_rule_state(rule_name)
            button.setChecked(enabled)


class TitleSubtitleExtractor(QObject):
    """Extracts title and subtitle from text for metadata."""
    
    # Signals
    title_subtitle_changed = Signal(str, str)  # title, subtitle
    
    def __init__(self, smart_formatter: SmartFormatter, parent=None):
        """Initialize title/subtitle extractor."""
        super().__init__(parent)
        
        self.smart_formatter = smart_formatter
        self.current_title = ""
        self.current_subtitle = ""
        
        # Connect to formatter changes
        self.smart_formatter.formatting_changed.connect(self._on_formatting_changed)
    
    def _on_formatting_changed(self):
        """Handle formatting changes and extract title/subtitle."""
        title, subtitle = self.smart_formatter.get_current_title_subtitle()
        
        # Only emit if changed
        if title != self.current_title or subtitle != self.current_subtitle:
            self.current_title = title
            self.current_subtitle = subtitle
            self.title_subtitle_changed.emit(title, subtitle)
    
    def get_current_title_subtitle(self) -> Tuple[str, str]:
        """Get current title and subtitle."""
        return self.current_title, self.current_subtitle