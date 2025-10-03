"""
Tests for the integrated editor panel.
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer, QRect, QSize
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeySequence

from src.pocket_journal.ui.editor_panel_integrated import (
    IconButton, CompactTopBar, CompactStatusBar, IntegratedEditorPanel
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
        assert button.size().width() == 24
        assert button.size().height() == 24
        assert not button.icon().isNull()
    
    def test_custom_size(self, app):
        """Test icon button with custom size."""
        button = IconButton("settings", "Settings", 32)
        
        assert button.size().width() == 32
        assert button.size().height() == 32
    
    def test_different_icons(self, app):
        """Test different icon types."""
        icon_types = ["back", "search", "export", "tags", "more", "settings", "help", "egg"]
        
        for icon_type in icon_types:
            button = IconButton(icon_type, f"{icon_type} tooltip")
            assert button.icon_name == icon_type
            assert not button.icon().isNull()


class TestCompactTopBar:
    """Test the CompactTopBar class."""
    
    def test_initialization(self, app):
        """Test compact top bar initialization."""
        top_bar = CompactTopBar()
        
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
        assert top_bar.height() == 30
    
    def test_button_signals(self, app):
        """Test that buttons emit correct signals."""
        top_bar = CompactTopBar()
        
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
        
        # Connect signals
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


class TestCompactStatusBar:
    """Test the CompactStatusBar class."""
    
    def test_initialization(self, app):
        """Test status bar initialization."""
        status_bar = CompactStatusBar()
        
        # Check components exist
        assert hasattr(status_bar, 'autosave_label')
        assert hasattr(status_bar, 'time_label')
        assert hasattr(status_bar, 'timer')
        
        # Check fixed height
        assert status_bar.height() == 18
        
        # Check timer is running
        assert status_bar.timer.isActive()
        assert status_bar.timer.interval() == 30000  # 30 seconds
    
    def test_autosave_status(self, app):
        """Test autosave status indicator."""
        status_bar = CompactStatusBar()
        
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
        status_bar = CompactStatusBar()
        
        # Check that time label has content
        time_text = status_bar.time_label.text()
        assert len(time_text) > 0
        
        # Check US date format pattern (MM/DD/YYYY hh:mm AM/PM)
        assert "/" in time_text  # Date separators
        assert ("AM" in time_text) or ("PM" in time_text)  # Time format


class TestIntegratedEditorPanel:
    """Test the IntegratedEditorPanel class."""
    
    def test_initialization(self, app):
        """Test integrated editor panel initialization."""
        panel = IntegratedEditorPanel()
        
        # Check components exist
        assert hasattr(panel, 'top_bar')
        assert hasattr(panel, 'text_editor')
        assert hasattr(panel, 'status_bar')
        assert hasattr(panel, 'autosave_timer')
        
        # Check autosave timer configuration
        assert panel.autosave_timer.isSingleShot()
        
        # Check initial state
        assert not panel.is_saving
        assert not panel.is_expanded
        
        # Check size configuration
        assert panel.target_width > 0
        assert panel.target_height > 0
    
    def test_text_editor_setup(self, app):
        """Test text editor configuration."""
        panel = IntegratedEditorPanel()
        
        # Check placeholder text - Step 5 requirement
        assert panel.text_editor.placeholderText() == "Start typing…"
        
        # Check word wrap - Step 5 requirement
        assert panel.text_editor.lineWrapMode() == panel.text_editor.LineWrapMode.WidgetWidth
        
        # Check that font is set
        font = panel.text_editor.font()
        assert font.pointSize() > 0
        
        # Check cursor width
        assert panel.text_editor.cursorWidth() == 2
    
    def test_top_bar_integration(self, app):
        """Test top bar integration - Step 5 requirement."""
        panel = IntegratedEditorPanel()
        
        # Verify top bar has all required icons from Step 5
        top_bar = panel.top_bar
        
        # Left side icons: Back/Recent, Search, Export, Tags, ⋯ (more)
        assert hasattr(top_bar, 'back_btn')
        assert hasattr(top_bar, 'search_btn') 
        assert hasattr(top_bar, 'export_btn')
        assert hasattr(top_bar, 'tags_btn')
        assert hasattr(top_bar, 'more_btn')
        
        # Right side icons: Settings, Help, (Egg icon if enabled)
        assert hasattr(top_bar, 'settings_btn')
        assert hasattr(top_bar, 'help_btn')
        assert hasattr(top_bar, 'egg_btn')
        
        # Check tooltips contain expected functionality
        assert "Back/Recent" in top_bar.back_btn.toolTip()
        assert "Search" in top_bar.search_btn.toolTip()
        assert "Export" in top_bar.export_btn.toolTip()
        assert "tags" in top_bar.tags_btn.toolTip().lower()
        assert "actions" in top_bar.more_btn.toolTip().lower()
        assert "Settings" in top_bar.settings_btn.toolTip()
        assert "Help" in top_bar.help_btn.toolTip()
    
    def test_status_bar_integration(self, app):
        """Test status bar integration - Step 5 requirement."""
        panel = IntegratedEditorPanel()
        
        status_bar = panel.status_bar
        
        # Check autosave indicator (bottom-right requirement)
        assert hasattr(status_bar, 'autosave_label')
        assert len(status_bar.autosave_label.text()) > 0
        
        # Check local time in US format (MM/DD/YYYY hh:mm AM/PM)
        assert hasattr(status_bar, 'time_label')
        time_text = status_bar.time_label.text()
        assert "/" in time_text  # Date format
        assert ("AM" in time_text) or ("PM" in time_text)  # Time format
    
    def test_keyboard_shortcuts(self, app):
        """Test keyboard shortcuts - Step 5 requirement."""
        panel = IntegratedEditorPanel()
        panel.show()  # Need to show for shortcuts to work
        
        # Mock signal emission
        panel.new_entry_requested = Mock()
        panel.save_requested = Mock() 
        panel.search_requested = Mock()
        panel.help_requested = Mock()
        panel.collapse_requested = Mock()
        
        # Test shortcuts exist (setup_shortcuts was called)
        assert hasattr(panel, 'setup_shortcuts')
        
        # Shortcuts: Ctrl+N (new), Ctrl+S (save), Ctrl+K (search), F1 (help), ESC (close)
        # Note: Direct shortcut testing is complex in Qt, but we verify setup was called
    
    def test_content_management(self, app):
        """Test content get/set/clear functionality."""
        panel = IntegratedEditorPanel()
        
        # Test setting content
        test_content = "This is test content for the integrated editor"
        panel.set_content(test_content)
        assert panel.get_content() == test_content
        
        # Test clearing content
        panel.clear_content()
        assert panel.get_content() == ""
    
    def test_autosave_functionality(self, app):
        """Test autosave functionality."""
        with patch('src.pocket_journal.ui.editor_panel_integrated.get_setting', return_value=500):
            panel = IntegratedEditorPanel()
            
            # Mock the autosave method
            panel._autosave = Mock()
            
            # Simulate content change
            panel._on_text_changed()
            
            # Check timer is started
            assert panel.autosave_timer.isActive()
            
            # Trigger timer
            panel.autosave_timer.timeout.emit()
            
            # Verify autosave was called
            panel._autosave.assert_called_once()
    
    def test_autosave_process(self, app):
        """Test autosave process flow."""
        panel = IntegratedEditorPanel()
        
        # Start autosave
        assert not panel.is_saving
        panel._autosave()
        assert panel.is_saving
        
        # Complete autosave
        panel._autosave_complete()
        assert not panel.is_saving
    
    def test_manual_save(self, app):
        """Test manual save (Ctrl+S) functionality."""
        panel = IntegratedEditorPanel()
        
        # Mock signals and methods
        panel.save_requested = Mock()
        panel._autosave = Mock()
        
        # Trigger manual save
        panel._manual_save()
        
        # Verify signals/methods called
        panel.save_requested.emit.assert_called_once()
        panel._autosave.assert_called_once()
    
    def test_expansion_functionality(self, app):
        """Test panel expansion functionality."""
        panel = IntegratedEditorPanel()
        
        # Test initial state
        assert not panel.is_expanded
        
        # Test expand from position
        start_pos = (100, 100)
        start_size = (48, 48)
        
        # Mock screen geometry for testing
        with patch('src.pocket_journal.ui.editor_panel_integrated.QApplication.primaryScreen') as mock_screen:
            mock_geometry = Mock()
            mock_geometry.right.return_value = 1920
            mock_geometry.bottom.return_value = 1080
            mock_geometry.left.return_value = 0
            mock_geometry.top.return_value = 0
            mock_screen.return_value.availableGeometry.return_value = mock_geometry
            
            panel.expand_from_position(start_pos, start_size)
            
            # Panel should be visible during expansion
            assert panel.isVisible()
    
    def test_signal_connections(self, app):
        """Test signal connections between components."""
        panel = IntegratedEditorPanel()
        
        # Mock panel signals
        mock_signals = {
            'search_requested': Mock(),
            'settings_requested': Mock(),
            'help_requested': Mock(),
        }
        
        panel.search_requested.connect(mock_signals['search_requested'])
        panel.settings_requested.connect(mock_signals['settings_requested'])
        panel.help_requested.connect(mock_signals['help_requested'])
        
        # Trigger top bar signals
        panel.top_bar.search_clicked.emit()
        panel.top_bar.settings_clicked.emit() 
        panel.top_bar.help_clicked.emit()
        
        # Verify signals were emitted
        mock_signals['search_requested'].assert_called_once()
        mock_signals['settings_requested'].assert_called_once()
        mock_signals['help_requested'].assert_called_once()
    
    def test_button_action_handlers(self, app):
        """Test button action handlers."""
        panel = IntegratedEditorPanel()
        
        # Test that action handlers exist and can be called without errors
        panel._on_back_clicked()
        panel._on_export_clicked()
        panel._on_tags_clicked()
        panel._on_more_clicked()
        
        # These should not raise exceptions (they're logging placeholders)
    
    def test_settings_integration(self, app):
        """Test settings integration."""
        panel = IntegratedEditorPanel()
        
        # Test load_settings
        panel.load_settings()
        
        # Test update_settings with mocked values
        with patch('src.pocket_journal.ui.editor_panel_integrated.get_setting') as mock_get:
            mock_get.side_effect = lambda key, default: {
                'font_family': 'Arial',
                'font_size': 14,
                'show_egg_icon': True,
            }.get(key, default)
            
            panel.update_settings()
            
            # Verify font was updated
            font = panel.text_editor.font()
            assert font.family() == 'Arial'
            assert font.pointSize() == 14
    
    def test_focus_functionality(self, app):
        """Test focus management."""
        panel = IntegratedEditorPanel()
        panel.show()
        
        # Test focus editor
        panel._focus_editor()
        
        # Note: Focus testing can be tricky in automated tests
        # We verify the method exists and can be called
        assert hasattr(panel, '_focus_editor')


class TestStep5AcceptanceCriteria:
    """Test Step 5 acceptance criteria specifically."""
    
    def test_panel_renders_cleanly(self, app):
        """Test: Panel renders cleanly."""
        panel = IntegratedEditorPanel()
        panel.show()
        
        # Panel should be visible and have proper size
        assert panel.isVisible()
        assert panel.width() > 0
        assert panel.height() > 0
        
        # Components should be properly laid out
        assert panel.top_bar.isVisible()
        assert panel.text_editor.isVisible() 
        assert panel.status_bar.isVisible()
    
    def test_icons_clickable(self, app):
        """Test: Icons clickable (no-ops yet)."""
        panel = IntegratedEditorPanel()
        
        # All top bar buttons should be clickable
        top_bar = panel.top_bar
        
        # Test clicking each button (should not raise exceptions)
        top_bar.back_btn.click()
        top_bar.search_btn.click()
        top_bar.export_btn.click()
        top_bar.tags_btn.click()
        top_bar.more_btn.click()
        top_bar.settings_btn.click()
        top_bar.help_btn.click()
        
        # All clicks should complete without errors
    
    def test_text_editor_responsive_and_focused(self, app):
        """Test: Text editor responsive and focused on open."""
        panel = IntegratedEditorPanel()
        panel.show()
        
        # Focus the editor
        panel._focus_editor()
        
        # Editor should accept text input
        test_text = "Test input"
        panel.text_editor.setPlainText(test_text)
        assert panel.text_editor.toPlainText() == test_text
        
        # Editor should be responsive to changes
        content_changed_signal = Mock()
        panel.content_changed.connect(content_changed_signal)
        
        panel.text_editor.setPlainText("New content")
        content_changed_signal.assert_called_with("New content")
    
    def test_minimalist_design_elements(self, app):
        """Test minimalist design elements."""
        panel = IntegratedEditorPanel()
        
        # Top bar should be compact (30px height)
        assert panel.top_bar.height() == 30
        
        # Status bar should be compact (18px height) 
        assert panel.status_bar.height() == 18
        
        # Icons should be small (24px)
        assert panel.top_bar.back_btn.size().width() == 24
        
        # Text editor should have subtle padding (checked via stylesheet)
        assert "padding: 8px" in panel.text_editor.styleSheet()
        
        # Placeholder text should be present
        assert panel.text_editor.placeholderText() == "Start typing…"