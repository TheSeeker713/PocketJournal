"""
Tests for Step 7 smart formatting functionality.
"""

import pytest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextCharFormat, QFont

from src.pocket_journal.core.smart_formatting import (
    SmartFormatter, FormattingToggleManager, TitleSubtitleExtractor, FormatRule
)
from src.pocket_journal.ui.formatting_toolbar import (
    FormattingToggleButton, SmartFormattingToolbar
)


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


class TestSmartFormatter:
    """Test the SmartFormatter class."""
    
    def test_smart_formatter_initialization(self, app):
        """Test smart formatter initialization."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        assert formatter.text_editor == text_editor
        assert formatter.original_text == ""
        assert formatter.title == ""
        assert formatter.subtitle == ""
        assert len(formatter.rules) > 0
    
    def test_formatting_rules_creation(self, app):
        """Test formatting rules are created correctly."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Check essential rules exist
        expected_rules = [
            'all_caps', 'emphatic_exclamation', 'important_phrases',
            'parentheticals', 'note_lines', 'action_lines',
            'bullet_lists', 'numbered_lists'
        ]
        
        for rule_name in expected_rules:
            assert rule_name in formatter.rules
            rule = formatter.rules[rule_name]
            assert isinstance(rule, FormatRule)
            assert rule.pattern
            assert rule.format_type
    
    def test_title_subtitle_parsing(self, app):
        """Test title and subtitle parsing from text."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Test with clear sentences
        text = "This is my title. This is my subtitle. This is body content."
        title, subtitle = formatter.parse_title_subtitle(text)
        
        assert title == "This is my title."
        assert subtitle == "This is my subtitle."
        
        # Test with markdown headers
        text = "# My Title\n\nThis is my subtitle. More content here."
        title, subtitle = formatter.parse_title_subtitle(text)
        
        assert title == "My Title"
        assert subtitle == "This is my subtitle."
        
        # Test with single sentence
        text = "Only one sentence here."
        title, subtitle = formatter.parse_title_subtitle(text)
        
        assert title == "Only one sentence here."
        assert subtitle == ""
    
    def test_rule_toggling(self, app):
        """Test formatting rule toggling."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Test toggling a rule
        original_state = formatter.get_rule_state('all_caps')
        new_state = formatter.toggle_rule('all_caps')
        
        assert new_state == (not original_state)
        assert formatter.get_rule_state('all_caps') == new_state
        
        # Test toggling back
        final_state = formatter.toggle_rule('all_caps')
        assert final_state == original_state
    
    def test_text_change_handling(self, app):
        """Test text change handling and formatting."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Mock apply_formatting to track calls
        formatter.apply_formatting = Mock()
        
        # Set text content
        test_text = "This is IMPORTANT text! Some (parenthetical) content."
        text_editor.setPlainText(test_text)
        
        # Simulate text change
        formatter._on_text_changed()
        
        # Check that formatting was triggered (may be called multiple times due to signals)
        assert formatter.apply_formatting.called
        
        # Check title/subtitle extraction
        assert formatter.title == "This is IMPORTANT text!"
        assert formatter.subtitle == "Some (parenthetical) content."
    
    def test_all_caps_rule(self, app):
        """Test ALL-CAPS formatting rule."""
        text_editor = QTextEdit()
        text_editor.setPlainText("This is IMPORTANT and CRITICAL information!")
        
        formatter = SmartFormatter(text_editor)
        
        # Check that rule pattern matches expected content
        rule = formatter.rules['all_caps']
        import re
        matches = list(re.finditer(rule.pattern, text_editor.toPlainText()))
        
        # Should match "IMPORTANT" and "CRITICAL" (both ≥4 chars)
        assert len(matches) == 2
        assert matches[0].group() == "IMPORTANT"
        assert matches[1].group() == "CRITICAL"
    
    def test_parenthetical_rule(self, app):
        """Test parenthetical formatting rule."""
        text_editor = QTextEdit()
        text_editor.setPlainText("This has (some parenthetical content) in it.")
        
        formatter = SmartFormatter(text_editor)
        
        rule = formatter.rules['parentheticals']
        import re
        matches = list(re.finditer(rule.pattern, text_editor.toPlainText()))
        
        assert len(matches) == 1
        assert matches[0].group() == "(some parenthetical content)"
    
    def test_note_action_lines(self, app):
        """Test NOTE: and ACTION: line formatting."""
        text_editor = QTextEdit()
        text_editor.setPlainText("NOTE: This is important\nACTION: Do this task\nRegular content")
        
        formatter = SmartFormatter(text_editor)
        
        # Test NOTE: rule
        note_rule = formatter.rules['note_lines']
        import re
        note_matches = list(re.finditer(note_rule.pattern, text_editor.toPlainText(), re.MULTILINE))
        assert len(note_matches) == 1
        assert "NOTE: This is important" in note_matches[0].group()
        
        # Test ACTION: rule  
        action_rule = formatter.rules['action_lines']
        action_matches = list(re.finditer(action_rule.pattern, text_editor.toPlainText(), re.MULTILINE))
        assert len(action_matches) == 1
        assert "ACTION: Do this task" in action_matches[0].group()
    
    def test_list_formatting_rules(self, app):
        """Test bullet and numbered list formatting."""
        text_editor = QTextEdit()
        text_editor.setPlainText("- First bullet\n* Second bullet\n1. First number\n2. Second number")
        
        formatter = SmartFormatter(text_editor)
        
        # Test bullet lists
        bullet_rule = formatter.rules['bullet_lists']
        import re
        bullet_matches = list(re.finditer(bullet_rule.pattern, text_editor.toPlainText(), re.MULTILINE))
        assert len(bullet_matches) == 2
        
        # Test numbered lists
        numbered_rule = formatter.rules['numbered_lists']
        numbered_matches = list(re.finditer(numbered_rule.pattern, text_editor.toPlainText(), re.MULTILINE))
        assert len(numbered_matches) == 2


class TestFormattingToggleButton:
    """Test the FormattingToggleButton class."""
    
    def test_button_initialization(self, app):
        """Test formatting toggle button initialization."""
        button = FormattingToggleButton("test_rule", "Test Rule Description", "bold")
        
        assert button.rule_name == "test_rule"
        assert button.description == "Test Rule Description"
        assert button.icon_type == "bold"
        assert button.isCheckable()
        assert button.isChecked()  # Default enabled
    
    def test_button_icon_types(self, app):
        """Test different button icon types."""
        icon_types = ["bold", "italic", "underline", "list", "caps", "exclamation", "parentheses", "note"]
        
        for icon_type in icon_types:
            button = FormattingToggleButton(f"rule_{icon_type}", f"Test {icon_type}", icon_type)
            assert not button.icon().isNull()


class TestSmartFormattingToolbar:
    """Test the SmartFormattingToolbar class."""
    
    def test_toolbar_initialization(self, app):
        """Test formatting toolbar initialization."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        toolbar = SmartFormattingToolbar(formatter)
        
        assert toolbar.smart_formatter == formatter
        assert len(toolbar.toggle_buttons) > 0
        assert hasattr(toolbar, 'all_button')
        assert hasattr(toolbar, 'none_button')
    
    def test_toolbar_button_registration(self, app):
        """Test toolbar button registration with toggle manager."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        toolbar = SmartFormattingToolbar(formatter)
        
        # Check that buttons are registered for key rules
        expected_buttons = ['all_caps', 'emphatic_exclamation', 'parentheticals', 'note_lines', 'bullet_lists']
        
        for rule_name in expected_buttons:
            if rule_name in formatter.rules:
                assert rule_name in toolbar.toggle_buttons
    
    def test_all_none_buttons(self, app):
        """Test All/None functionality."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        toolbar = SmartFormattingToolbar(formatter)
        
        # Test disable all
        toolbar._disable_all_rules()
        for rule in formatter.rules.values():
            assert not rule.enabled
        
        # Test enable all
        toolbar._enable_all_rules()
        for rule in formatter.rules.values():
            assert rule.enabled


class TestTitleSubtitleExtractor:
    """Test the TitleSubtitleExtractor class."""
    
    def test_extractor_initialization(self, app):
        """Test title/subtitle extractor initialization."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        extractor = TitleSubtitleExtractor(formatter)
        
        assert extractor.smart_formatter == formatter
        assert extractor.current_title == ""
        assert extractor.current_subtitle == ""
    
    def test_title_subtitle_change_detection(self, app):
        """Test title/subtitle change detection."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        extractor = TitleSubtitleExtractor(formatter)
        
        # Mock signal
        extractor.title_subtitle_changed = Mock()
        
        # Simulate text change that updates title/subtitle
        formatter.title = "New Title"
        formatter.subtitle = "New Subtitle"
        extractor._on_formatting_changed()
        
        # Should emit signal with new title/subtitle
        extractor.title_subtitle_changed.emit.assert_called_once_with("New Title", "New Subtitle")
        
        # Check internal state updated
        assert extractor.current_title == "New Title"
        assert extractor.current_subtitle == "New Subtitle"


class TestStep7AcceptanceCriteria:
    """Test Step 7 acceptance criteria specifically."""
    
    def test_first_two_sentences_populate_metadata(self, app):
        """Test: Parse user text into sentences; map 1st sentence to H1 (title), 2nd to H2 (subtitle)."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Test with clear sentence structure
        text = "My daily journal entry. Today was a good day. More content follows here."
        title, subtitle = formatter.parse_title_subtitle(text)
        
        assert title == "My daily journal entry."
        assert subtitle == "Today was a good day."
        
        # Test that original text remains unchanged
        text_editor.setPlainText(text)
        formatter._on_text_changed()
        
        assert text_editor.toPlainText() == text  # Original text unchanged
    
    def test_live_styling_rules(self, app):
        """Test: Live styling in the editor viewport for various patterns."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Test text with various formatting patterns
        test_text = """IMPORTANT note here!
This has (parenthetical content) in it.
NOTE: This is a note line
ACTION: This is an action item
- First bullet point
* Second bullet point
1. First numbered item
2. Second numbered item"""
        
        text_editor.setPlainText(test_text)
        
        # Check that all relevant rules have patterns that match
        import re
        
        # ALL-CAPS rule
        caps_matches = list(re.finditer(formatter.rules['all_caps'].pattern, test_text))
        assert len(caps_matches) >= 1  # Should match "IMPORTANT"
        
        # Parenthetical rule
        paren_matches = list(re.finditer(formatter.rules['parentheticals'].pattern, test_text))
        assert len(paren_matches) == 1
        
        # Note lines
        note_matches = list(re.finditer(formatter.rules['note_lines'].pattern, test_text, re.MULTILINE))
        assert len(note_matches) == 1
        
        # Action lines
        action_matches = list(re.finditer(formatter.rules['action_lines'].pattern, test_text, re.MULTILINE))
        assert len(action_matches) == 1
        
        # Bullet lists
        bullet_matches = list(re.finditer(formatter.rules['bullet_lists'].pattern, test_text, re.MULTILINE))
        assert len(bullet_matches) == 2
        
        # Numbered lists
        numbered_matches = list(re.finditer(formatter.rules['numbered_lists'].pattern, test_text, re.MULTILINE))
        assert len(numbered_matches) == 2
    
    def test_inline_toggles_disable_rules(self, app):
        """Test: Provide inline toggles in the tiny toolbar to disable specific rules session-wide."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        toolbar = SmartFormattingToolbar(formatter)
        
        # Test rule toggling
        rule_name = 'all_caps'
        original_state = formatter.get_rule_state(rule_name)
        
        # Toggle via toolbar button
        if rule_name in toolbar.toggle_buttons:
            button = toolbar.toggle_buttons[rule_name]
            button.setChecked(not original_state)
            button.toggled.emit(not original_state)
            
            # Rule state should change
            assert formatter.get_rule_state(rule_name) == (not original_state)
    
    def test_settings_persistence(self, app):
        """Test: Persist toggle settings."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        # Test save/load settings
        original_states = {name: rule.enabled for name, rule in formatter.rules.items()}
        
        # Change some states
        formatter.toggle_rule('all_caps')
        formatter.toggle_rule('parentheticals')
        
        # Save settings
        formatter.save_rule_settings()
        
        # Create new formatter and load settings
        new_formatter = SmartFormatter(QTextEdit())
        
        # Check that states were persisted
        assert new_formatter.get_rule_state('all_caps') != original_states['all_caps']
        assert new_formatter.get_rule_state('parentheticals') != original_states['parentheticals']
    
    def test_raw_text_unchanged(self, app):
        """Test: Raw saved text remains user-authored."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        original_text = "This is IMPORTANT text with (parenthetical) content!"
        text_editor.setPlainText(original_text)
        
        # Apply formatting
        formatter._on_text_changed()
        formatter.apply_formatting()
        
        # Raw text should remain unchanged
        assert formatter.original_text == original_text
        assert text_editor.toPlainText() == original_text
    
    def test_styling_applies_and_reverts_with_toggles(self, app):
        """Test: Styling visibly applies/reverts with toggles."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        text_editor.setPlainText("This is IMPORTANT text!")
        
        # Enable rule and apply formatting
        formatter.rules['all_caps'].enabled = True
        formatter.apply_formatting = Mock()
        
        # Toggle rule off
        formatter.toggle_rule('all_caps')
        
        # Should trigger formatting reapplication
        formatter.apply_formatting.assert_called()
        
        # Rule should be disabled
        assert not formatter.get_rule_state('all_caps')
        
        # Toggle back on
        formatter.toggle_rule('all_caps')
        
        # Rule should be enabled again
        assert formatter.get_rule_state('all_caps')
    
    def test_deterministic_rule_based_formatting(self, app):
        """Test: Formatting is deterministic and rule-based."""
        text_editor = QTextEdit()
        formatter = SmartFormatter(text_editor)
        
        test_text = "IMPORTANT: This is (very important) content!"
        
        # Apply formatting multiple times
        for _ in range(3):
            text_editor.setPlainText(test_text)
            formatter._on_text_changed()
            
            # Text should remain consistent
            assert text_editor.toPlainText() == test_text
            
            # Title extraction should be consistent
            title, subtitle = formatter.parse_title_subtitle(test_text)
            assert title == "IMPORTANT: This is (very important) content!"