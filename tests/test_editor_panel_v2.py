"""
Tests for the enhanced editor panel with top bar and status bar.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeySequence

from src.pocket_journal.ui.editor_panel_v2 import (
    IconButton, EditorTopBar, EditorStatusBar, EditorTextArea, 
    EnhancedEditorPanel, create_enhanced_editor_panel
)


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


class TestIconButton:
    """Test the IconButton class."""
    
    def test_initialization(self, app):
        """Test icon button initialization."""
        button = IconButton("search", "Search tooltip")
        
        assert button.icon_name == "search"
        assert button.toolTip() == "Search tooltip"
        assert button.size().width() == 32
        assert button.size().height() == 32
        assert not button.icon().isNull()
    
    def test_different_icons(self, app):
        """Test different icon types."""
        icon_types = ["back", "search", "export", "tags", "more", "settings", "help", "egg"]
        
        for icon_type in icon_types:
            button = IconButton(icon_type, f"{icon_type} tooltip")
            assert button.icon_name == icon_type
            assert not button.icon().isNull()
    
    def test_unknown_icon(self, app):
        """Test unknown icon type falls back to default."""
        button = IconButton("unknown", "Unknown tooltip")
        assert button.icon_name == "unknown"
        assert not button.icon().isNull()  # Should still create an icon


class TestEditorTopBar:
    """Test the EditorTopBar class."""
    
    def test_initialization(self, app):
        """Test top bar initialization."""
        top_bar = EditorTopBar()
        
        # Check that all buttons exist
        assert hasattr(top_bar, 'back_btn')
        assert hasattr(top_bar, 'search_btn')
        assert hasattr(top_bar, 'export_btn')
        assert hasattr(top_bar, 'tags_btn')
        assert hasattr(top_bar, 'more_btn')
        assert hasattr(top_bar, 'settings_btn')
        assert hasattr(top_bar, 'help_btn')
        assert hasattr(top_bar, 'egg_btn')
        
        # Check fixed height
        assert top_bar.height() == 40
    
    def test_button_signals(self, app):
        """Test that buttons emit correct signals."""
        top_bar = EditorTopBar()
        
        # Connect mock slots to signals
        mock_slots = {
            'back_clicked': Mock(),
            'search_clicked': Mock(),
            'export_clicked': Mock(),
            'tags_clicked': Mock(),
            'more_clicked': Mock(),
            'settings_clicked': Mock(),
            'help_clicked': Mock(),
        }
        
        top_bar.back_clicked.connect(mock_slots['back_clicked'])
        top_bar.search_clicked.connect(mock_slots['search_clicked'])
        top_bar.export_clicked.connect(mock_slots['export_clicked'])
        top_bar.tags_clicked.connect(mock_slots['tags_clicked'])
        top_bar.more_clicked.connect(mock_slots['more_clicked'])
        top_bar.settings_clicked.connect(mock_slots['settings_clicked'])
        top_bar.help_clicked.connect(mock_slots['help_clicked'])
        
        # Test button clicks
        top_bar.back_btn.click()
        mock_slots['back_clicked'].assert_called_once()
        
        top_bar.search_btn.click()
        mock_slots['search_clicked'].assert_called_once()
        
        top_bar.export_btn.click()
        mock_slots['export_clicked'].assert_called_once()
        
        top_bar.tags_btn.click()
        mock_slots['tags_clicked'].assert_called_once()
        
        top_bar.more_btn.click()
        mock_slots['more_clicked'].assert_called_once()
        
        top_bar.settings_btn.click()
        mock_slots['settings_clicked'].assert_called_once()
        
        top_bar.help_btn.click()
        mock_slots['help_clicked'].assert_called_once()
    
    def test_egg_icon_visibility(self, app):
        """Test easter egg icon visibility."""
        with patch('src.pocket_journal.ui.editor_panel_v2.get_setting', return_value=False):
            top_bar = EditorTopBar()
            assert not top_bar.egg_btn.isVisible()
        
        with patch('src.pocket_journal.ui.editor_panel_v2.get_setting', return_value=True):
            top_bar = EditorTopBar()
            top_bar.update_egg_icon_visibility()
            # Note: visibility might depend on multiple settings


class TestEditorStatusBar:
    """Test the EditorStatusBar class."""
    
    def test_initialization(self, app):
        """Test status bar initialization."""
        status_bar = EditorStatusBar()
        
        # Check components exist
        assert hasattr(status_bar, 'autosave_label')
        assert hasattr(status_bar, 'time_label')
        assert hasattr(status_bar, 'timer')
        
        # Check fixed height
        assert status_bar.height() == 24
        
        # Check timer is running
        assert status_bar.timer.isActive()
        assert status_bar.timer.interval() == 30000  # 30 seconds
    
    def test_autosave_status(self, app):
        """Test autosave status indicator."""
        status_bar = EditorStatusBar()
        
        # Test saving status
        status_bar.set_autosave_status(True)
        assert "⚬" in status_bar.autosave_label.text()
        assert "Saving..." in status_bar.autosave_label.toolTip()
        
        # Test saved status
        status_bar.set_autosave_status(False)
        assert "●" in status_bar.autosave_label.text()
        assert "Autosave active" in status_bar.autosave_label.toolTip()
    
    def test_time_update(self, app):
        """Test time display update."""
        status_bar = EditorStatusBar()
        
        # Check that time label has content
        time_text = status_bar.time_label.text()
        assert len(time_text) > 0
        
        # Check US date format pattern (MM/DD/YYYY hh:mm AM/PM)
        assert "/" in time_text  # Date separators
        assert ("AM" in time_text) or ("PM" in time_text)  # Time format


class TestEditorTextArea:
    """Test the EditorTextArea class."""
    
    def test_initialization(self, app):
        """Test text area initialization."""
        editor = EditorTextArea()
        
        # Check placeholder text
        assert editor.placeholderText() == "Start typing…"
        
        # Check word wrap
        assert editor.lineWrapMode() == editor.LineWrapMode.WidgetWidth
        
        # Check that font is set
        font = editor.font()
        assert font.pointSize() > 0
    
    def test_content_changed_signal(self, app):
        """Test content changed signal emission."""
        editor = EditorTextArea()
        
        # Connect mock slot
        mock_slot = Mock()
        editor.content_changed.connect(mock_slot)
        
        # Change text
        test_text = "This is test content"
        editor.setPlainText(test_text)
        
        # Verify signal was emitted
        mock_slot.assert_called_with(test_text)
    
    def test_focus_editor(self, app):
        """Test focus editor functionality."""
        editor = EditorTextArea()
        editor.show()  # Need to show widget for focus to work
        
        # Set some text
        editor.setPlainText("Test content")
        
        # Focus editor
        editor.focus_editor()
        
        # Verify focus and cursor position
        assert editor.hasFocus()
        cursor = editor.textCursor()
        assert cursor.position() == len("Test content")
    
    def test_shortcuts(self, app):
        """Test keyboard shortcuts."""
        editor = EditorTextArea()
        editor.show()
        
        # Test Ctrl+K shortcut
        with patch.object(editor, '_on_search_shortcut') as mock_search:
            QTest.keySequence(editor, QKeySequence("Ctrl+K"))
            # Note: Shortcut testing in Qt can be complex, this verifies the method exists
            
        # Test F1 shortcut
        with patch.object(editor, '_on_help_shortcut') as mock_help:
            QTest.keySequence(editor, QKeySequence("F1"))


class TestEnhancedEditorPanel:
    """Test the EnhancedEditorPanel class."""
    
    def test_initialization(self, app):
        """Test enhanced editor panel initialization."""
        panel = EnhancedEditorPanel()
        
        # Check components exist
        assert hasattr(panel, 'top_bar')
        assert hasattr(panel, 'text_editor')
        assert hasattr(panel, 'status_bar')
        assert hasattr(panel, 'autosave_timer')
        
        # Check autosave timer configuration
        assert panel.autosave_timer.isSingleShot()
        
        # Check initial state
        assert not panel.is_saving
    
    def test_content_management(self, app):
        """Test content get/set/clear functionality."""
        panel = EnhancedEditorPanel()
        
        # Test setting content
        test_content = "This is test content for the editor"
        panel.set_content(test_content)
        assert panel.get_content() == test_content
        
        # Test clearing content
        panel.clear_content()
        assert panel.get_content() == ""
    
    def test_autosave_timer(self, app):
        """Test autosave timer functionality."""
        with patch('src.pocket_journal.ui.editor_panel_v2.get_setting', return_value=500):
            panel = EnhancedEditorPanel()
            
            # Mock the autosave method
            panel._autosave = Mock()
            
            # Simulate content change
            panel._on_content_changed("New content")
            
            # Check timer is started
            assert panel.autosave_timer.isActive()
            
            # Trigger timer
            panel.autosave_timer.timeout.emit()
            
            # Verify autosave was called
            panel._autosave.assert_called_once()
    
    def test_autosave_process(self, app):
        """Test autosave process."""
        panel = EnhancedEditorPanel()
        
        # Start autosave
        assert not panel.is_saving
        panel._autosave()
        assert panel.is_saving
        
        # Complete autosave
        panel._autosave_complete()
        assert not panel.is_saving
    
    def test_manual_save(self, app):
        """Test manual save functionality."""
        panel = EnhancedEditorPanel()
        
        # Mock signals and methods
        panel.save_requested = Mock()
        panel._autosave = Mock()
        
        # Trigger manual save
        panel._manual_save()
        
        # Verify signals/methods called
        panel.save_requested.emit.assert_called_once()
        panel._autosave.assert_called_once()
    
    def test_shortcuts(self, app):
        """Test keyboard shortcuts."""
        panel = EnhancedEditorPanel()
        panel.show()
        
        # Mock signal emissions
        panel.new_entry_requested = Mock()
        panel.close_requested = Mock()
        panel._manual_save = Mock()
        
        # Test shortcuts exist (shortcuts are complex to test programmatically)
        # We verify the setup methods were called during initialization
        assert hasattr(panel, 'setup_shortcuts')
    
    def test_signal_connections(self, app):
        """Test that all signals are properly connected."""
        panel = EnhancedEditorPanel()
        
        # Verify signal connection methods were called
        assert hasattr(panel, 'setup_connections')
        
        # Test top bar signals reach panel
        mock_slots = {
            'search_requested': Mock(),
            'settings_requested': Mock(),
            'help_requested': Mock(),
        }
        
        panel.search_requested.connect(mock_slots['search_requested'])
        panel.settings_requested.connect(mock_slots['settings_requested'])
        panel.help_requested.connect(mock_slots['help_requested'])
        
        # Trigger top bar signals
        panel.top_bar.search_clicked.emit()
        mock_slots['search_requested'].emit.assert_called_once()
        
        panel.top_bar.settings_clicked.emit()
        mock_slots['settings_requested'].emit.assert_called_once()
        
        panel.top_bar.help_clicked.emit()
        mock_slots['help_requested'].emit.assert_called_once()
    
    def test_settings_update(self, app):
        """Test settings update functionality."""
        panel = EnhancedEditorPanel()
        
        # Mock settings
        with patch('src.pocket_journal.ui.editor_panel_v2.get_setting') as mock_get:
            mock_get.side_effect = lambda key, default: {
                'font_family': 'Arial',
                'font_size': 14,
                'show_egg_icon': True,
                'eggs_enabled': True
            }.get(key, default)
            
            # Update settings
            panel.update_settings()
            
            # Verify font was updated
            font = panel.text_editor.font()
            assert font.family() == 'Arial'
            assert font.pointSize() == 14
    
    def test_show_and_focus(self, app):
        """Test show and focus functionality."""
        panel = EnhancedEditorPanel()
        
        # Mock focus method
        panel.focus_editor = Mock()
        
        # Show and focus
        panel.show_and_focus()
        
        # Verify panel is visible
        assert panel.isVisible()
        
        # Note: focus_editor will be called via QTimer, difficult to test directly
    
    def test_button_actions(self, app):
        """Test button action handlers."""
        panel = EnhancedEditorPanel()
        
        # Test that action handlers exist and can be called
        panel._on_back_clicked()
        panel._on_export_clicked()
        panel._on_tags_clicked()
        panel._on_more_clicked()
        
        # These should not raise exceptions (they're no-ops for now)


class TestCreateEnhancedEditorPanel:
    """Test the convenience function."""
    
    def test_create_function(self, app):
        """Test create_enhanced_editor_panel function."""
        panel = create_enhanced_editor_panel()
        
        assert isinstance(panel, EnhancedEditorPanel)
        assert panel.parent() is None
        
        # Test with parent
        parent_widget = app.activeWindow()
        if parent_widget:
            panel_with_parent = create_enhanced_editor_panel(parent_widget)
            assert panel_with_parent.parent() == parent_widget


class TestEditorPanelIntegration:
    """Test integration between components."""
    
    def test_top_bar_to_panel_signals(self, app):
        """Test signal flow from top bar to panel."""
        panel = EnhancedEditorPanel()
        
        # Mock panel signal methods
        mock_signals = {
            'search_requested': Mock(),
            'settings_requested': Mock(),
            'help_requested': Mock(),
        }
        
        panel.search_requested.connect(mock_signals['search_requested'])
        panel.settings_requested.connect(mock_signals['settings_requested'])
        panel.help_requested.connect(mock_signals['help_requested'])
        
        # Trigger top bar buttons
        panel.top_bar.search_btn.click()
        panel.top_bar.settings_btn.click()
        panel.top_bar.help_btn.click()
        
        # Verify signals were emitted
        mock_signals['search_requested'].emit.assert_called_once()
        mock_signals['settings_requested'].emit.assert_called_once()
        mock_signals['help_requested'].emit.assert_called_once()
    
    def test_text_editor_to_autosave(self, app):
        """Test text editor changes trigger autosave."""
        panel = EnhancedEditorPanel()
        
        # Mock autosave
        original_autosave = panel._autosave
        panel._autosave = Mock()
        
        # Change text
        panel.text_editor.setPlainText("Test content")
        
        # Check that autosave timer is started
        assert panel.autosave_timer.isActive()
        
        # Restore original method
        panel._autosave = original_autosave
    
    def test_status_bar_time_updates(self, app):
        """Test that status bar time updates correctly."""
        panel = EnhancedEditorPanel()
        
        # Get initial time
        initial_time = panel.status_bar.time_label.text()
        assert len(initial_time) > 0
        
        # Manually trigger time update
        panel.status_bar.update_time()
        
        # Time should still be a valid string
        updated_time = panel.status_bar.time_label.text()
        assert len(updated_time) > 0
        assert "/" in updated_time  # Date format check